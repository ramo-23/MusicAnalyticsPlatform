import { TestBed } from '@angular/core/testing';

import { MusicApi } from './music-api';

describe('MusicApi', () => {
  let service: MusicApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MusicApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
