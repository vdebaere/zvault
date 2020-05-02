# zvault #

The `zvault` utility relies on native encryption of ZFS datasets to
provide various encrypted vaults in the user's home directory. These
vaults can be locked, unlocked independently from each other.

## Dependencies ##

`zvault` is written in Python 3 and relies on the following Python
modules:

  - pyzfs
  - python-gnupg
  - python-xdg

In its current implementation, `zvault`relies on PolicyKit's `pkexec`
utility to execute privileged operations and on GnuPG to (optionaly)
encrypt keys for caching purposes.

## Usage ##

### Create and Destroy a vault ###

    zvault create [--parent parent_dataset] [--gpg-key [keyid]] vault_path

Creates a zvault at `vault_path`. The `vault_path` parameter is
resolved relative to the user's home directory.

The vault is created as a child of the dataset specified with the
`parent` option. If the `parent` option is omitted, `zvault` attempts
to create the vault as a child of the dataset hosting the home
directory of the user. In that case, any component of vault_path will
be created if necessary as a separate dataset.

By default, this command will prompt for a passphrase. The option
`gpg-key` makes zvault autogenerate a random key, which is stored in a
file encrypted to recipient `keyid`. The random key is generated by
gnupg.

    zvault destroy [-f] vault_path

Destroy a zvault at `vault_path`. The option `-f` forces the locking
of the vault before destroying it.

### Lock and unlock a vault ###

    zvault unlock vault_path

Unlock the vault at `vault_path`

    zvault lock vault_path

Lock the vault at `vault_path`.
