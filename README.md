# mariomoura.pzserver

Ansible collection with a single role, `pzserver`, that installs and manages a
Project Zomboid dedicated server on Debian/Ubuntu:

- steamcmd install and server install/update
- `<servername>.ini`, spawn points and spawn regions generated from variables
- JVM settings and a systemd unit
- daily world backup and hourly `players.db` backup via systemd timers
- graceful stops: players are warned over RCON and the world is saved before
  any update or config-triggered restart (bundled stdlib-only `pzrcon.py`, also
  handy for ad-hoc commands: `~steam/pzrcon.py 127.0.0.1 27015 <password> players`)

## Install

```yaml
# requirements.yml
collections:
  - name: https://github.com/MarioMoura/ansible-pzserver.git
    type: git
    version: main
```

```bash
ansible-galaxy collection install -r requirements.yml
```

## Usage

```yaml
- hosts: zomboid
  become: true
  roles:
    - role: mariomoura.pzserver.pzserver
      vars:
        pzserver_admin_password: "{{ admin_password }}"
        pzserver_jvm_max_heap: "12g"
        pzserver_config:
          server:
            public_name: "My Server"
            password: "{{ server_password }}"
            max_players: 16
          rcon:
            password: "{{ rcon_password }}"
          mods:
            - { wid: 3641048285, mid: ItemCondition_KingEJ, name: "Item Condition Overlay" }
```

Config-only run (don't stop the server for a steamcmd update; changed files
still trigger a warned restart):

```bash
ansible-playbook site.yml -e pzserver_skip_update=true
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `pzserver_user` | `steam` | System user that owns and runs the server |
| `pzserver_home` | `/home/steam` | Base directory |
| `pzserver_install_dir` | `{{ pzserver_home }}/pzserver` | Server files |
| `pzserver_profile_dir` | `{{ pzserver_home }}/profile` | `-Duser.home`; config lives in `Zomboid/Server` below it |
| `pzserver_servername` | `servertest` | Name passed to `-servername`; also the config file prefix |
| `pzserver_service_name` | `pzserver` | systemd unit name (backup units are `<name>-backup*`) |
| `pzserver_admin_password` | `""` | Admin password passed on first start |
| `pzserver_jvm_max_heap` | `8g` | `-Xmx` |
| `pzserver_skip_update` | `false` | Skip steamcmd update and the pre-update stop |
| `pzserver_restart_warning` | `60` | Seconds of RCON warning before stop/restart; `0` disables |
| `pzserver_rcon_timeout` | `30` | Socket timeout in seconds for RCON calls |
| `pzserver_backup_enabled` | `true` | Install backup scripts and timers |
| `pzserver_backup_keep_days` / `pzserver_backup_db_keep_hours` | `7` / `48` | Retention |
| `pzserver_backup_on_calendar` / `pzserver_backup_db_on_calendar` | `daily` / `hourly` | systemd `OnCalendar` |
| `pzserver_spawnpoints` | `[]` | Custom spawn points (`profession`, `worldX`, `worldY`, `posX`, `posY`) |
| `pzserver_spawnregions` | 4 vanilla towns | Built-in regions (`name`, `file`, `enabled`) |
| `pzserver_custom_spawnregions` | `[]` | Regions pointing at the generated spawnpoints file |
| `pzserver_config` | `{}` | Server settings, merged recursively over `pzserver_config_defaults` |

`pzserver_config_defaults` in `roles/pzserver/defaults/main.yml` lists every
supported key grouped by section (`server`, `network`, `pvp`, `player`,
`safehouse`, `faction`, `sleep`, `game`, `vehicle`, `voice`, `anticheat`,
`steam`, `rcon`, `discord`, `backup`, `logging`, `misc`, `ids`, `radio`,
`bad_word_filter`, `mods`, `map`, `welcome_message`, `webhook_address`).

Mods take `wid` (Workshop ID) and `mid` (mod ID, a string or a list of
strings); `name` is informational.
