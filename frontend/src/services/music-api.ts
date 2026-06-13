import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TrackMetric } from '../models/track-metric';

@Injectable({
  providedIn: 'root',
})

export class MusicApiService {
  private http = inject(HttpClient);

  // Point to the backend API endpoint for track metrics
  private apiUrl = 'https://localhost:7183/api/Analytics';

  getTopTracks(): Observable<TrackMetric[]> {
    return this.http.get<TrackMetric[]>(`${this.apiUrl}/top-tracks`);
  }
}
