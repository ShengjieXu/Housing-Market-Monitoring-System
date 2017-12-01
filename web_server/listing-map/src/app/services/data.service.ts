import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { Statistics, Listings } from '../models/data.model';

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' })
};

@Injectable()
export class DataService {

  private statsAPI = 'api/v1/markets/stats/average';
  private listingsAPIBase = 'api/v1/markets/listings/';

  constructor(private http: HttpClient) { }

  getStatistics(): Observable<Statistics> {
    return this.http.get<Statistics>(this.statsAPI)
    .pipe(
      catchError(this.handleError('getStatistics', {type: 'average', payloads: []}))
    );
  }

  getRegions(): any {
    return this.http.get<any>('assets/regions.json')
    .pipe(
      catchError(this.handleError('getRegions', []))
    );
  }

  getListings(region: string): Observable<Listings> {
    return this.http.get<Listings>(this.listingsAPIBase + region)
    .pipe(
      catchError(this.handleError('getListings', {region: '', payloads: []}))
    );
  }

  /**
   * Handle Http operation that failed.
   * Let the app continue.
   * @param operation - name of the operation that failed
   * @param result - optional value to return as the observable result
   */
  private handleError<T> (operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

}
