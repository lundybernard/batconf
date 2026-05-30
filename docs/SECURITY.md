# BatConf Security Policy

## Security contact information
To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.

## Release signing keys
BatConf releases are signed with GPG. Verify downloaded artifacts against
the detached `.asc` signatures attached to each
[GitHub Release](https://github.com/lundybernard/batconf/releases), and
verify the `vX.Y.Z` git tag with `git tag -v vX.Y.Z`.

Each maintainer who cuts releases signs with their own key. The canonical
list of authorized signing keys is the
[`KEYS`](https://github.com/lundybernard/batconf/blob/main/KEYS) file at
the repository root. Import it once, then verify:

```
gpg --import KEYS
git tag -v vX.Y.Z
gpg --verify batconf-X.Y.Z.tar.gz.asc batconf-X.Y.Z.tar.gz
```

Authorized signers (see `KEYS` for the full public keys):

| Maintainer | Fingerprint | Authorized |
|------------|-------------|------------|
| Lundy Bernard | `10D0375D 76138F64 C966CE81 E6A1871D 072F9BB1` | 2026-06-07 – |

The keys are also mirrored to a keyserver for convenience:

```
gpg --keyserver keys.openpgp.org --recv-keys {FINGERPRINT}
```
