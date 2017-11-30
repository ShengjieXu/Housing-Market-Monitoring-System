export class Statistics {
  type: string;
  payloads: Payload[];
}

export class Payload {
  region: string;
  count: number;
  data: number;
}
