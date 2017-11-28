import { Statistic } from './models/data.model';

export const STATISTICS: Statistic[] = [{
  of: {
    name: 'losangeles',
    geo: {
      lat: 34.021,
      lnt: -118.692
    },
    radius: 150000
  },
  type: 'average',
  amount: 2560
}, {
  of: {
    name: 'sfbay',
    geo: {
      lat: 37.876,
      lnt: -123.542
    },
    radius: 150000
  },
  type: 'average',
  amount: 3200
}, {
  of: {
    name: 'newyork',
    geo: {
      lat: 40.698,
      lnt: -74.26
    },
    radius: 150000
  },
  type: 'average',
  amount: 2400
}, {
  of: {
    name: 'dallas',
    geo: {
      lat: 32.821,
      lnt: -97.012
    },
    radius: 150000
  },
  type: 'average',
  amount: 1432
}, {
  of: {
    name: 'seattle',
    geo: {
      lat: 47.613,
      lnt: -122.482
    },
    radius: 150000
  },
  type: 'average',
  amount: 2120
}, {
  of: {
    name: 'denver',
    geo: {
      lat: 39.765,
      lnt: -104.995
    },
    radius: 150000
  },
  type: 'average',
  amount: 1900
}, {
  of: {
    name: 'austin',
    geo: {
      lat: 30.308,
      lnt: -98.034
    },
    radius: 150000
  },
  type: 'average',
  amount: 1200
}];
