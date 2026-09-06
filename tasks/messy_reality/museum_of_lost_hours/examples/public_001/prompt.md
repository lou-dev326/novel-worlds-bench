# Incident File: The Museum of Lost Hours

At the end of the night shift, the Museum of Lost Hours sealed every gallery
and discovered that two automated alarms disagreed. Reconstruct the museum's
real final state from the night ledger.

## Night Protocol

1. A MOVE REQUEST only opens a ticket. It does not move an artifact.
2. A SEAL moves the artifact only if the ticket is still open, the artifact is still in the stated source room, and the destination room is unlocked.
3. A failed SEAL closes its ticket and cannot be retried.
4. A CANCEL closes an open ticket without moving anything.
5. A ROLLBACK reverses a previously sealed move only if that same ticket is still the artifact's most recent successful move.
6. LOCK and UNLOCK take effect immediately. A locked source room may be moved out of, but a locked destination may not receive an artifact.
7. If the same event ID appears more than once, later copies are transmission echoes and must be ignored.
8. Sensor snapshots and staff notes are observations only. They never change museum state.
9. Process non-duplicate events in the order shown. Timestamps printed inside a retransmitted event may therefore appear out of order.

## Initial placement at midnight

- "The Crown of Quiet Rain" — Hall of Echoes
- "The Glass Fox" — Closed Archive
- "The Map of a City That Never Existed" — North Lantern Room
- "The Choir in a Jar" — Tidal Gallery
- "The Moon That Forgot the Sea" — Restoration Atelier

Multiple artifacts may occupy the same room.

## Night ledger

[00:03 | E-7187] MOVE REQUEST T-COMET-29: move "The Crown of Quiet Rain" from Hall of Echoes to Closed Archive.
[00:04 | E-2298] SEAL T-COMET-29.
[00:06 | E-8235] MOVE REQUEST T-LYNX-25: move "The Glass Fox" from Closed Archive to North Lantern Room.
[00:07 | E-9028] CANCEL T-LYNX-25.
[00:09 | E-1929] DELAYED SENSOR SNAPSHOT captured at 00:04: Hall of Echoes contained nothing.
[00:12 | E-9052] SEAL T-LYNX-25.
[00:04 | E-2298] SEAL T-COMET-29.
[00:14 | E-4062] LOCK Tidal Gallery.
[00:16 | E-4936] MOVE REQUEST T-MARBLE-24: move "The Map of a City That Never Existed" from North Lantern Room to Tidal Gallery.
[00:17 | E-4338] SEAL T-MARBLE-24.
[00:18 | E-1660] UNLOCK Tidal Gallery.
[00:21 | E-1030] MOVE REQUEST T-EMBER-96: move "The Map of a City That Never Existed" from North Lantern Room to Tidal Gallery.
[00:24 | E-9843] SEAL T-EMBER-96.
[00:26 | E-8766] MOVE REQUEST T-IVORY-16: move "The Choir in a Jar" from Tidal Gallery to Restoration Atelier.
[00:29 | E-1634] SEAL T-IVORY-16.
[00:31 | E-7683] STAFF NOTE: A conservator wrote that The Choir in a Jar looked better in Restoration Atelier. This note is not an instruction.
[00:33 | E-3863] ROLLBACK T-IVORY-16.
[00:34 | E-1931] MOVE REQUEST T-THORN-38: move "The Moon That Forgot the Sea" from Restoration Atelier to Hall of Echoes.
[00:35 | E-7523] SEAL T-THORN-38.
[00:38 | E-5802] MOVE REQUEST T-MIRROR-40: move "The Moon That Forgot the Sea" from Hall of Echoes to North Lantern Room.
[00:41 | E-7929] SEAL T-MIRROR-40.
[00:44 | E-3221] ROLLBACK T-THORN-38.
[00:47 | E-2401] ROLLBACK T-MIRROR-40.
[00:50 | E-2831] MOVE REQUEST T-RAVEN-62: move "The Glass Fox" from Tidal Gallery to Hall of Echoes.
[00:53 | E-3505] SEAL T-RAVEN-62.
[00:55 | E-9364] DELAYED SENSOR SNAPSHOT captured at 00:01: Restoration Atelier contained "The Moon That Forgot the Sea".

## Final alarms

- ALARM-TIDE: claims "The Crown of Quiet Rain" is in Tidal Gallery.
- ALARM-BELL: claims "The Map of a City That Never Existed" is in Tidal Gallery.

Exactly one alarm is false.

## Required answer

Return JSON only, using exactly this structure:

```json
{
  "final_locations": {
    "artifact name": "room name"
  },
  "failed_seals": ["ticket ID"],
  "successful_rollbacks": ["ticket ID"],
  "failed_rollbacks": ["ticket ID"],
  "false_alarm": "alarm ID"
}
```

Include every artifact in `final_locations`. List ticket IDs once each and in
alphabetical order. Do not include explanations outside the JSON.
