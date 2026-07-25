.. currentmodule:: batconf

GPG Signing Key Setup
=====================

Releases are signed with GPG so that users can verify an artifact really
came from a BatConf maintainer and was not tampered with in transit. Each
maintainer who cuts releases uses **their own** key; we never share a
private key between people. Do the one-time setup below before your first
release.

Key model: primary key + signing subkey
----------------------------------------

A GPG "key" is really a *keypair set*: one **primary key** plus one or more
**subkeys**. We use this split deliberately:

* The **primary key** is your long-lived identity. It is *certify-only*
  (capability ``C``) — its only job is to vouch for your subkeys and your
  user ID (name + email). It rarely needs to be online, so we keep it
  **offline** (encrypted backup, not on your daily machine). If it is
  never exposed, your identity never has to change.
* A **signing subkey** (capability ``S``) is what actually signs tags and
  release artifacts day to day. It lives on your working machine (or a
  hardware token). If it is lost or compromised you can revoke or replace
  *just the subkey* while keeping the same identity and fingerprint.

The primary key's **fingerprint** (40 hex characters) is the stable thing
users trust. Rotating a subkey does not change it.

.. note::

   **Why expiry?** We set a ~1 year expiry on the signing subkey as a
   dead-man's switch: if a maintainer disappears or loses access, the key
   stops being trusted on its own. Expiry is **not** revocation — a
   signature made while the key was valid stays valid forever, so expiring
   a key never invalidates past releases. You *extend* the expiry before it
   lapses (see Maintenance below); you do not re-key.

Generate your key
-----------------

1. Generate the primary key, choosing "(8) RSA (set your own
   capabilities)" or the ECC equivalent, and set it to **certify only**
   (toggle off Sign/Encrypt/Authenticate), with **no expiry** on the
   primary:

   .. code-block:: bash

      gpg --expert --full-generate-key

   Use your real name and the email you commit with. Pick a strong
   passphrase.

2. Note the primary key fingerprint:

   .. code-block:: bash

      gpg --fingerprint --list-keys "Your Name"

   Export it as an environment variable for the commands below:

   .. code-block:: bash

      FPR=<your 40-char fingerprint, no spaces>

3. Add a dedicated **signing subkey** with a 1 year expiry:

   .. code-block:: bash

      gpg --quick-add-key "$FPR" rsa4096 sign 1y

Back up and prepare for disaster
---------------------------------

Do this immediately, before you sign anything:

* **Generate a revocation certificate** and store it offline (separate from
  the key). If your key is ever compromised, this lets you publicly revoke
  it even if you have lost the key itself:

  .. code-block:: bash

     gpg --output ~/batconf-revoke.asc --gen-revoke "$FPR"

* **Back up the primary secret key** to offline, encrypted storage:

  .. code-block:: bash

     gpg --export-secret-keys --armor "$FPR" > ~/batconf-primary-secret.asc

  Keep this off your daily machine. For day-to-day work you only need the
  subkey.

Publish your public key
------------------------

Users and co-maintainers need your **public** key to verify signatures.
Publish it two ways:

1. **In-repo KEYS file (canonical).** Append your *armored* public key to
   the :gh-file:`KEYS <KEYS>` file at the repo root. "Armored" means
   ASCII-armored: the binary key wrapped in printable text (a
   ``-----BEGIN PGP PUBLIC KEY BLOCK-----`` block) so it survives being
   committed to git and copied around.

   .. code-block:: bash

      gpg --armor --export "$FPR" >> KEYS

   Commit this. The ``KEYS`` file is the trust anchor users import once:
   ``gpg --import KEYS``. We prefer it over keyservers because it is
   versioned, reviewed, and cannot be poisoned by third parties.

2. **Keyserver (convenience mirror).** Also send it to a keyserver so
   ``--recv-keys`` works for users who expect that flow:

   .. code-block:: bash

      gpg --keyserver keys.openpgp.org --send-keys "$FPR"

   (For ``keys.openpgp.org`` you must also confirm the verification email it
   sends, or only the raw key without your user ID is distributed.)

Finally, record your name, primary fingerprint, and the dates you became /
ceased to be an authorized signer in
:gh-file:`docs/SECURITY.md <docs/SECURITY.md>` so downstream users know
which keys sign BatConf releases.

Maintaining your identity and signing keys
------------------------------------------

* **Extend the subkey before it expires** (do *not* let it lapse, and do
  *not* generate a brand-new primary key):

  .. code-block:: bash

     gpg --quick-set-expire "$FPR" 1y '*'   # extend all subkeys by 1y

  Then re-publish: append the refreshed key to ``KEYS`` (replacing your old
  block) and ``--send-keys`` again. Verifiers pick up the new expiry on next
  import.

* **Rotate the signing subkey** periodically (e.g. yearly) by adding a new
  signing subkey and expiring the old one. The primary fingerprint — and
  therefore the trust users have in you — is unchanged.

* **If a key is compromised**, publish the revocation certificate
  (``gpg --import ~/batconf-revoke.asc && gpg --send-keys "$FPR"``), remove
  the key from ``KEYS``, and note it in ``docs/SECURITY.md``. Past releases
  signed before the compromise remain verifiable; that is expected.

Multiple maintainers
--------------------

Every maintainer who cuts releases follows the steps above with their own
key, and adds their own armored public key to ``KEYS``. Verifiers trust the
whole set of keys in ``KEYS``. When someone stops maintaining, remove their
key block from ``KEYS`` going forward — signatures they made while
authorized stay valid, which is correct. Record who signed each release in
the changelog entry (e.g. ``Signed by: Name <fingerprint>``) so there is a
human-readable audit trail of which key signed which version.
