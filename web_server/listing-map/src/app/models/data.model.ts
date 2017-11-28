export class Statistic {
  of: Region;
  type: string;
  amount: number;
}

export class Region {
  name: string;
  geo: Geo;
  radius: number;
}

export class Geo {
  lat: number;
  lnt: number;
}
