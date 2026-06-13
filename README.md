# Last.fm Analytics Data Pipeline & Dashboard

An end-to-end, enterprise-grade data ingestion and visualisation platform that extracts crowdsourced music data from the Last.fm REST API, processes it through a lightweight analytical data warehouse, and serves it through a reactive, paginated frontend dashboard.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Key Features](#key-features)
- [Data Flow](#data-flow)
- [Project Structure](#project-structure)
- [Local Setup Instructions](#local-setup-instructions)
- [API Reference](#api-reference)
- [Data Governance](#data-governance)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

This project demonstrates a complete analytics workflow, from data extraction to dashboard visualisation.

It ingests top track data from the Last.fm API, transforms and normalises it into a DuckDB-based star schema, exposes analytical queries through a .NET REST API, and presents the results in an Angular dashboard.

The application is designed around clear separation of concerns, lightweight tooling, and analytical performance.

---

## System Architecture

The application follows a decoupled three-tier architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Last.fm REST API                         │
│                  Crowdsourced Music Metadata                    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Tier 1 — Data Engineering Layer                │
│                        Python 3 ETL Scripts                     │
│                                                                 │
│   extract.py  ──►  Flatten JSON  ──►  load.py  ──►  DuckDB     │
│                                                                 │
│   Star Schema: Fact_Metrics | Dim_Track | Dim_Artist            │
└──────────────────────────────┬──────────────────────────────────┘
                               │ File I/O (.duckdb)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Tier 2 — API Layer                         │
│               C# .NET 10 / ASP.NET Core / Dapper               │
│                                                                 │
│   Controllers  ──►  Dapper Queries  ──►  DuckDB Connection      │
│   Async endpoints, minimal overhead, Swagger UI                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │ JSON over HTTP
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                Tier 3 — Client Presentation Layer               │
│                   Angular 18 Standalone Components              │
│                                                                 │
│   HTTP Client  ──►  Signals State  ──►  Computed Pagination     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Data Extraction | Python 3, `requests` | REST API ingestion and JSON parsing |
| Data Warehouse | DuckDB | Embedded analytical database using a star schema |
| Backend API | C# .NET 10, ASP.NET Core | Asynchronous REST API server |
| Micro-ORM | Dapper | Lightweight SQL-to-object mapping |
| Frontend | Angular 18 | Signal-driven reactive UI |
| API Documentation | Swagger / OpenAPI | Auto-generated endpoint documentation |

---

## Key Features

### Star Schema Design

Raw JSON payloads from the Last.fm API are flattened and normalised into a traditional star schema during ingestion. This separates descriptive attributes from measurable metrics, enabling efficient analytical querying.

```
Dim_Artist          Fact_Metrics          Dim_Track
──────────          ────────────          ─────────
artist_id  ◄─────── artist_id             track_id
artist_name         track_id  ───────────► track_name
listeners           play_count            duration
                    listeners             mbid
                    rank                  url
                    ingested_at
```

### Asynchronous Micro-ORM API

The API is read-only, making heavy ORM change tracking unnecessary. Dapper was selected for direct SQL execution, minimal abstraction overhead, fast analytical reads, and simple mapping between SQL results and C# models.

### Signal-Driven Angular UI

The frontend uses Angular 18 Signals for reactive state management.

```typescript
tracks = signal<Track[]>([]);

paginatedTracks = computed(() =>
  this.tracks().slice(
    (this.currentPage() - 1) * this.pageSize,
    this.currentPage() * this.pageSize
  )
);
```

This removes the need for additional observable subscriptions in the component layer and keeps state management simple.

### Client-Side Pagination

The dashboard paginates large datasets directly in the browser using computed signals. This reduces unnecessary API requests while keeping the UI highly responsive.

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Last.fm REST API                         │
│              GET /chart.getTopTracks?limit=200                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ JSON Response
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                          extract.py                             │
│                                                                 │
│   Parses JSON response · Flattens nested artist/track objects   │
│   Writes raw records to staging list                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │ Staging Records
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                           load.py                               │
│                                                                 │
│   Opens DuckDB connection · Creates Star Schema tables          │
│   Resolves surrogate keys · Inserts normalised records          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ File I/O (.duckdb)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    music_analytics.duckdb                       │
│                                                                 │
│   Embedded analytical store · Star schema · Fact_Metrics        │
│   Dim_Track · Dim_Artist · Full referential integrity           │
└──────────────────────────────┬──────────────────────────────────┘
                               │ DuckDB .NET Connector
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MusicAnalytics.Api                        │
│                                                                 │
│   Executes parameterised Dapper queries · Serialises to JSON    │
│   Exposes REST endpoints on https://localhost:5001              │
└──────────────────────────────┬──────────────────────────────────┘
                               │ JSON over HTTP
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Angular Dashboard                          │
│                                                                 │
│   HttpClient fetches data · Stores state in Signals             │
│   Computed Signals drive pagination · Renders metrics           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
lastfm-analytics/
│
├── data_pipeline/
│   ├── src/
│   │   ├── extract.py
│   │   └── load.py
│   ├── music_analytics.duckdb
│   └── requirements.txt
│
├── api/
│   └── MusicAnalytics.Api/
│       ├── Controllers/
│       │   └── TracksController.cs
│       ├── Models/
│       │   ├── Track.cs
│       │   └── Artist.cs
│       ├── Data/
│       │   └── DuckDbConnectionFactory.cs
│       ├── Program.cs
│       └── MusicAnalytics.Api.csproj
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── components/
│   │       │   └── dashboard/
│   │       ├── services/
│   │       │   └── tracks.service.ts
│   │       └── app.component.ts
│   ├── angular.json
│   └── package.json
│
└── README.md
```

---

## Local Setup Instructions

### Prerequisites

Ensure the following are installed before proceeding:

- [Python 3.10+](https://www.python.org/downloads/)
- [.NET 10 SDK](https://dotnet.microsoft.com/download)
- [Node.js 20+](https://nodejs.org/) and npm
- [Angular CLI](https://angular.io/cli) (`npm install -g @angular/cli`)

---

### Step 1 — Build the Data Warehouse

Navigate to the data pipeline directory, create a virtual environment, and install dependencies.

```bash
cd data_pipeline

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install requests duckdb
```

Run the ETL pipeline to generate the `music_analytics.duckdb` file.

```bash
python src/extract.py
python src/load.py
```

---

### Step 2 — Launch the .NET API

Navigate to the API project, restore dependencies, and run the server.

```bash
cd ../api/MusicAnalytics.Api

dotnet restore
dotnet run
```

Swagger documentation will be available in your browser automatically. Ensure the DuckDB file has been generated before starting the API.

---

### Step 3 — Serve the Angular Dashboard

Open a new terminal, navigate to the frontend directory, and start the development server.

```bash
cd frontend

npm install
ng serve --open
```

The dashboard will open at `http://localhost:4200`.

---

## API Reference

Full documentation is available through Swagger UI at `https://localhost:5001/swagger` when the backend is running.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/tracks` | Returns all tracks with artist and play count metrics |
| `GET` | `/api/tracks/{id}` | Returns a single track by its surrogate key |
| `GET` | `/api/artists` | Returns all artists with aggregate listener counts |

All responses are returned as `application/json`. The API is read-only and does not expose mutation endpoints.

---

## Data Governance

### The Folksonomy Problem

Last.fm uses a folksonomy-based tagging system, meaning tags are generated by users rather than controlled by a central taxonomy. This can introduce data quality issues where tracks from one genre appear in unrelated genre charts due to inaccurate or inconsistent user-applied tags.

### Mitigation Approach

The current implementation treats genre tags as descriptive metadata only. Tags are not used for hard filtering or categorical grouping in the star schema. The analytical layer focuses strictly on measurable, quantitative metrics to avoid propagating folksonomy noise into the warehouse.

---

## Future Enhancements

- Add scheduled ingestion using APScheduler or Apache Airflow
- Add dynamic genre filtering parameters to the C# API
- Containerise the API and frontend using Docker with a `docker-compose.yml` for one-command local deployment
- Implement tag confidence scoring in the ETL layer to filter low-frequency, misattributed genre tags before warehouse load

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
