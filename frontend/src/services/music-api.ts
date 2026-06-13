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
  private apiUrl = 'https://amapiano-analytics-api.onrender.com/api/analytics';

  getTopTracks(): Observable<TrackMetric[]> {
    return this.http.get<TrackMetric[]>(`${this.apiUrl}/top-tracks`);
  }
}
