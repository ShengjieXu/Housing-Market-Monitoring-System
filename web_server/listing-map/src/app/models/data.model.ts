export class Statistics {
  type: string;
  payloads: Statistic[];
}

export class Statistic {
  region: string;
  count: number;
  data: number;
}

export class Listings {
  region: string;
  payloads: Listing[];
}

export class Listing {
  url: string;
  title: string;
  price: string;
  geo: Geo;
  bed: string;
  bath: string;
  available_date: string;
  img_url: string;
}

export class Geo {
  latitude: string;
  longitude: string;
}
