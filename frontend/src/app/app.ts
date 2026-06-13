import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { MusicApiService } from '../services/music-api';
import { TrackMetric } from '../models/track-metric';

@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  protected readonly title = signal('music-dashboard');

  // Inject our .NET API Service
  private musicService = inject(MusicApiService);

  // State Signals
  topTracks = signal<TrackMetric[]>([]);
  isLoading = signal<boolean>(true);

  // Pagination Signals
  currentPage = signal<number>(1);
  pageSize = signal<number>(10); // How many tracks per page

  // Computed signal: Automatically splices the topTracks array based on the current page
  paginatedTracks = computed(() => {
    const startIndex = (this.currentPage() - 1) * this.pageSize();
    const endIndex = startIndex + this.pageSize();
    return this.topTracks().slice(startIndex, endIndex);
  });

  // Computed signal: Calculates total number of pages needed
  totalPages = computed(() => Math.ceil(this.topTracks().length / this.pageSize()));

  ngOnInit() {
    this.fetchData();
  }

  fetchData() {
    this.musicService.getTopTracks().subscribe({
      next: (data) => {
        this.topTracks.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Data pipeline connection failed:', err);
        this.isLoading.set(false);
      }
    });
  }

  // Navigation Methods
  nextPage() {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.update(p => p + 1);
    }
  }

  prevPage() {
    if (this.currentPage() > 1) {
      this.currentPage.update(p => p - 1);
    }
  }
}