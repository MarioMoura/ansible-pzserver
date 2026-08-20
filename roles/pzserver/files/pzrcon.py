#!/usr/bin/env python3
"""Minimal Source RCON client: pzrcon.py HOST PORT PASSWORD COMMAND [COMMAND...]"""
import socket
import struct
import sys

AUTH, AUTH_RESPONSE, EXEC, RESPONSE = 3, 2, 2, 0


def send(sock, pid, ptype, body):
    payload = struct.pack("<ii", pid, ptype) + body.encode() + b"\x00\x00"
    sock.sendall(struct.pack("<i", len(payload)) + payload)


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed")
        buf += chunk
    return buf


def read(sock):
    (size,) = struct.unpack("<i", recv_exact(sock, 4))
    data = recv_exact(sock, size)
    pid, ptype = struct.unpack("<ii", data[:8])
    return pid, ptype, data[8:-2].decode(errors="replace")


def main():
    host, port, password, *commands = sys.argv[1:]
    with socket.create_connection((host, int(port)), timeout=10) as sock:
        send(sock, 1, AUTH, password)
        while True:
            pid, ptype, _ = read(sock)
            if ptype == AUTH_RESPONSE:
                break
        if pid == -1:
            sys.exit("authentication refused")
        for i, cmd in enumerate(commands, start=2):
            send(sock, i, EXEC, cmd)
            pid, _, body = read(sock)
            print(body.rstrip())


if __name__ == "__main__":
    main()
