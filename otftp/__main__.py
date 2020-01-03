import logging
import asyncio

from otftp.protocols import OberonTFTPServerProtocol
from otftp.cli_parser import parse_cli_arguments


def main():
    args = parse_cli_arguments()

    logging.info('Starting TFTP server on {addr}:{port}'.format(
        addr=args.host, port=args.port))

    timeouts = {
        bytes(k, encoding='ascii'): v
        for k, v in vars(args).items() if 'timeout' in k
    }
    loop = asyncio.get_event_loop()

    def _wakeup():
        """
        This method is used to wake up the loop at regular intervals,
        this is a workaround for the SIGINT issue: https://bugs.python.org/issue23057
        (affects python version < 3.8.1 on Windows)
        """
        loop.call_later(0.1, _wakeup)

    loop.call_later(0.1, _wakeup)

    listen = loop.create_datagram_endpoint(
        lambda: OberonTFTPServerProtocol(args.files_dir, args.host, loop, timeouts),
        local_addr=(args.host, args.port,))

    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info('Received signal, shutting down')

    transport.close()
    loop.close()


if __name__ == '__main__':
    main()
