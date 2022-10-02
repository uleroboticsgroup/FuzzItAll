"""
Definition of utilities for the authentication module.
"""

import logging

import paramiko as pmk
import paramiko.ssh_exception as pmk_e
import scp
import socket

import app.authentication.exceptions as fia_aue


class RemoteClient:
    # class based on: https://github.com/hackersandslackers/paramiko-tutorial
    """
    Client to handle connections and actions executed against a remote
    host (via SSH and SCP).

    Attributes
    ----------
    __ssh : paramiko.SSHClient
        SSH connection to perform actions on the remote host.
    __scp : scp.SCPClient
        SCP connection for file transfers between local and remote hosts.

    Methods
    -------
    __create_ssh_connection(str, int, str, str, paramiko.RSAKey) -> paramiko.SSHClient:
        Creates and establishes a SSH connection to a remote host with
        the given options.
    disconnect():
        Closes SSH & SCP connections.
    run_command(str) -> list:
        Executes a command on the remote host.
    upload_data(str, str):
        Transfer files from localhost to remote host.
    download_data(str, str):
        Transfer files from remote host to localhost.
    """

    # ----------------------------------------------------------------
    #   CONSTRUCTORS
    # ----------------------------------------------------------------

    def __init__(self, host: str, port: int, username: str, password: str,
                 rsa_key: pmk.RSAKey = None):
        """
        Default constructor.

        Parameters
        ----------
        host : str
            Server to connect to.
        port : int
            Server port to connect to.
        user : str
            Username to authenticate as.
        password : str
            Used for password authentication either associated to the user\
            or associated to the RSA key.
        rsa_key : paramiko.RSAKey
            Private key based on RSA algorithm.

        Raises
        ------
        app.authentication.exceptions.AuthenticationError -- Failed to\
            authenticate on the remote host.\\
        app.authentication.exceptions.RemoteCommunicationError -- Either\
            failed to connect/establish a connection to the remote host\
            or host SSH key did not match.
        """
        self.__logger = logging.getLogger(__name__)

        from pathlib import Path
        from flask import current_app
        self.__KNOWN_HOSTS = Path(current_app.instance_path, 'known_hosts')

        # create SSH & SCP connections
        self.__ssh = self.__create_ssh_connection(
            host, port, username, password, rsa_key)
        scp_aux_conn = self.__create_ssh_connection(
            host, port, username, password, rsa_key)
        self.__scp = scp.SCPClient(scp_aux_conn.get_transport())
        self.__logger.info(f'[RemoteClient] Successfully connected as '
                           f'{username}@{host}:{port}')

    # ----------------------------------------------------------------
    #   CONNECTION HANDLING METHODS
    # ----------------------------------------------------------------

    def __cache_ssh_key(self, host: str, port: int, ssh_key: pmk.RSAKey):
        """
        TODO (gonestco): description
        avoid AutoAddPolicy()!!! -- https://stackoverflow.com/questions/10670217/paramiko-unknown-server#43093883
        """
        # create a known_hosts file if it does not exist
        if not self.__KNOWN_HOSTS.exists():
            self.__KNOWN_HOSTS.open()

        # create a temporary client to load host keys
        client = pmk.SSHClient()
        client.load_host_keys(self.__KNOWN_HOSTS)
        host_keys = client.get_host_keys()

        # register the new ssh key if it does not exist
        if not host_keys.check(host, ssh_key):
            host_keys.add(f'[{host}]:{port}', 'ssh-rsa', ssh_key)
            host_keys.save(self.__KNOWN_HOSTS)

        client.close()

    def __create_ssh_connection(self, host: str, port: int,
                                username: str, password: str,
                                rsa_key: pmk.RSAKey = None) -> pmk.SSHClient:
        """
        Creates and establishes a SSH connection to a remote host with
        the given options.

        Parameters
        ----------
        host : str
            Server to connect to.
        port : int
            Server SSH port to connect to.
        username : str
            Username to authenticate as.
        password : str
            Password either associated to the username or associated to\
            the RSA key.
        rsa_key : paramiko.RSAKey
            Private RSA key to authenticate the user on the remote host.

        Returns
        -------
        client : paramiko.SSHClient
            SSH client to perform actions on remote host.

        Raises
        ------
        app.authentication.exceptions.AuthenticationError -- Failed to\
            authenticate on the remote host.\\
        app.authentication.exceptions.RemoteCommunicationError -- Either\
            failed to connect/establish a connection to the remote host\
            or host SSH key did not match.
        """
        try:
            client = pmk.SSHClient()
            # client.load_host_keys(self.__KNOWN_HOSTS)
            client.set_missing_host_key_policy(pmk.AutoAddPolicy())
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                pkey=rsa_key,
                timeout=5000,
                allow_agent=False,
                look_for_keys=False
            )
            return client
        except (pmk_e.AuthenticationException, pmk_e.NoValidConnectionsError) as e:
            msg = 'Authentication to the remote host failed.'
            self.__logger.error(f'[RemoteClient] {msg} Reason: {e}')
            raise fia_aue.AuthenticationError(msg)
        except (pmk_e.BadHostKeyException, pmk_e.SSHException) as e:
            msg = 'An error occurred while trying to connect to the remote host.'
            self.__logger.error(f'[RemoteClient] {msg} Reason: {e}')
            raise fia_aue.RemoteCommunicationError(msg)
        except (pmk_e.NoValidConnectionsError, socket.gaierror) as e:
            msg = 'Unknown host or bad port.'
            self.__logger.error(f'[RemoteClient] {msg}. Reason: {e}')
            raise fia_aue.RemoteCommunicationError(msg)

    def disconnect(self) -> None:
        """
        Closes SSH & SCP connections.

        Returns
        -------
        None
        """
        if self.__ssh:
            self.__ssh.close()
        if self.__scp:
            self.__scp.close()
        self.__logger.info(
            '[RemoteClient] Successfully disconnected from server.')

    # ----------------------------------------------------------------
    #   EXECUTABLE ACTIONS METHODS
    # ----------------------------------------------------------------

    def run(self, command: str) -> dict:
        """
        Executes a command on the remote host.

        Parameters
        ----------
        command : str
            Command to run.

        Returns
        -------
        command_out : dict
            Output of the command, consisting of the keys exit_status,\
            output and error.

        Raises
        ------
        app.authentication.exceptions.RemoteCommandError -- Failed to\
            run a command on the remote host.
        """
        try:
            stdin, stdout, stderr = self.__ssh.exec_command(command)
            command_out = dict(
                exit_code=stdout.channel.recv_exit_status(),
                output=[line.strip()
                        for line in stdout.readlines() if line != '\n'],
                error=[line.strip()
                       for line in stderr.readlines() if line != '\n']
            )
            return command_out

        except pmk.SSHException as e:
            msg = 'Failed to run a command on the remote host.'
            self.__logger.error(f'[RemoteClient] {msg} Reason: {e}')
            raise fia_aue.RemoteCommandError(msg)

    def upload_data(self, local_path: str, remote_path: str) -> None:
        """
        Transfer files from localhost to remote host.

        Parameters
        ----------
        local_path : str
            Path to retrieve from localhost.
        remote_path : str
            Path in which to receive files remotely.

        Returns
        -------
        None

        Raises
        ------
        app.authentication.exceptions.DataTransferError -- Data transfer failed.
        """
        try:
            self.__scp.put(
                files=local_path,
                remote_path=remote_path,
                recursive=True
            )
        except scp.SCPException as e:
            msg = 'Data transfer failed.'
            self.__logger.error(f'[RemoteClient] {msg} Reason: {e}')
            raise fia_aue.DataTransferError(msg)

    def download_data(self, remote_path: str, local_path: str) -> None:
        """
        Transfer files from remote host to localhost.

        Parameters
        ----------
        remote_path : str
            Path to retrieve from remote host.
        local_path : str
            Path in which to receive files locally.

        Returns
        -------
        None

        Raises
        ------
        app.authentication.exceptions.DataTransferError -- Data transfer failed.
        """
        try:
            self.__scp.get(
                remote_path=remote_path,
                local_path=local_path,
                recursive=True
            )
        except scp.SCPException as e:
            msg = 'Data transfer failed.'
            self.__logger.error(f'[RemoteClient] {msg} Reason: {e}')
            raise fia_aue.DataTransferError(msg)
