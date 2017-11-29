import { Injectable } from '@angular/core';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { Statistic } from '../models/data.model';
import { STATISTICS } from '../mock.data';

@Injectable()
export class DataService {

  constructor() { }

  getStatistics(): Observable<Statistic[]> {
    return of(STATISTICS);
  }

}
