import { Component, OnInit } from '@angular/core';

import { Statistic } from '../../models/data.model';
import { STATISTICS } from '../../mock.data';
import { element } from 'protractor';

declare const L: any;

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css']
})
export class MapComponent implements OnInit {
  defaultView: object = {
    name: 'US',
    geo: {
      lat: 39.096,
      lnt: -100.401
    },
    zoomLevel: 4
  };
  intervals: number[] = [1000, 1500, 2000, 2500, 3000, 3500];
  colors: string[] = ['#21313E', '#225760', '#258077', '#49AA80', '#87D27C', '#D7F574', '#D7F574'];

  map: any;
  circles = [];

  statistics: Statistic[] = [];

  constructor() { }

  ngOnInit() {
    this.loadMap();
    this.loadStats();
  }

  resetMap(): void {
    const lat = this.defaultView['geo']['lat'];
    const lnt = this.defaultView['geo']['lnt'];
    const zoomLevel = this.defaultView['zoomLevel'];
    this.map = L.map('map').setView([lat, lnt], zoomLevel);
  }

  loadMap(): void {
    this.resetMap();
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,' +
                     ' <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                     'Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 14,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoibGVtb25teXRoIiwiYSI6ImNqYWl0NXZ1bTIxb2czM3BsMzBjbGRlZDYifQ.ZXxe85ZoxDGMKhsGoGCjGg'
    }).addTo(this.map);
  }

  loadStats(): void {
    // TODO: make async
    this.statistics = STATISTICS;

    this.statistics.forEach(stat => {
      const name = stat['of']['name'];
      const lat = stat['of']['geo']['lat'];
      const lnt = stat['of']['geo']['lnt'];
      const radius = stat['of']['radius'];

      const type = stat['type'];
      const amount = stat['amount'];

      const circle = L.circle([lat, lnt], radius).addTo(this.map);

      this.circles.push(this.setCircleStyle(circle, amount));
    });
  }

  setCircleStyle(circle: any, amount: number): any {
    let i = 0;
    for (; i < this.intervals.length; i++) {
      if (amount <= this.intervals[i]) {
        return circle.setStyle({
          color: this.colors[i],
          fillColor: this.colors[i],
          fillOpacity: 0.5
        });
      }
    }
    return circle.setStyle({
      color: this.colors[i],
      fillColor: this.colors[i],
      fillOpacity: 0.5
    });
  }

}
