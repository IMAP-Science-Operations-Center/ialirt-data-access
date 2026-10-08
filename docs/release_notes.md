# I-ALiRT Release Notes

This page summarizes notable changes to I-ALiRT data, algorithms, ground station
coverage, and data access. I-ALiRT data is produced in real time and is not
reprocessed, so each entry lists the date the change took **effect**. Data
before that date was produced with the previous behavior.

Entries are newest first. Each entry has one of the following types:

- **Algorithm** – a change to how a data product is calculated
- **Data access** – a change to the API or to the `ialirt-data-access` tool
- **Ground station** – a station added to or removed from real-time coverage
- **Mission event** – a spacecraft or mission milestone that affects the data

Dates are in UTC and are accurate to the day.

---

## 2026-10-06 — MAG: updated coordinate frame
- **Type:** Algorithm
- **Affects:** MAG
- **Summary:** MAG vectors now use the SPICE-defined coordinate frames, including a new ecliptic frame (`IMAP_ECLIPMOD`). Values may shift slightly compared with earlier data.

## 2026-08-05 — Mopra ground station added
- **Type:** Ground station
- **Affects:** All instruments
- **Summary:** Mopra (Australia) packets are now ingested and Mopra contacts appear on the coverage plots, which adds real-time coverage.

## 2026-06-15 — CoDICE-Hi: spin angle added
- **Type:** Algorithm
- **Affects:** CoDICE-Hi
- **Summary:** CoDICE-Hi products now include a spin angle dimension.

## 2026-04-06 — CoDICE-Lo data restored
- **Type:** Algorithm
- **Affects:** CoDICE-Lo
- **Summary:** CoDICE-Lo real-time processing has been re-enabled (see 2026-02-06).

## 2026-04-02 — HIT data enabled
- **Type:** Data access
- **Affects:** HIT
- **Summary:** HIT real-time processing enabled after a flight software update.

## 2026-03-11 — UKSA ground station added
- **Type:** Ground station
- **Affects:** All instruments
- **Summary:** UK Space Agency (UKSA) packets are now ingested, and UKSA's tracking schedule is included in the coverage plots.

## 2026-02-26 — Archive query added to the API
- **Type:** Data access
- **Affects:** `ialirt-data-access` v0.7.0 and later
- **Summary:** Archived I-ALiRT CDF files can now be queried and downloaded. A `since` parameter for data queries followed in v0.8.0.

## 2026-02-06 — CoDICE-Lo temporarily removed
- **Type:** Algorithm
- **Affects:** CoDICE-Lo
- **Summary:** CoDICE-Lo processing was paused until an instrument flight software issue was fixed. It was restored on 2026-04-06.

## 2026-02-01 — Public data release
- **Type:** Data access
- **Affects:** All instruments
- **Summary:** I-ALiRT data from 2026-02-01 onward is publicly available without an API key. Data from before 2026-02-01 still requires an API key. Archived CDF files are now data version `001`.

## 2025-09-24 — Launch
- **Type:** Mission event
- **Summary:** IMAP launched. I-ALiRT real-time data collection began during commissioning. Production data access became the default in `ialirt-data-access` v0.5.0, released 2025-09-18.

## 2025-09-24 — Kiel ground station
- **Type:** Ground station
- **Affects:** All instruments
- **Summary:** Kiel (Germany) was added as an I-ALiRT ground station and was ready to receive real-time data at launch.
