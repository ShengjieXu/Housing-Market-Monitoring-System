import { Component, OnInit } from '@angular/core';

import { Statistic } from '../../models/data.model';
import { DataService } from '../../services/data.service';

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

  map: any;
  legend: any;
  info: any;
  circles = [];

  intervals: number[] = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500];

  statsType = 'Average';
  statistics: Statistic[] = [];

  constructor(private ds: DataService) { }

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

    this.initLegend();
  }

  loadStats(): void {
    // TODO: cleaning existing circles

    this.ds.getStatistics()
      .subscribe(statistics => this.statistics = statistics);

    this.statistics.forEach(stat => {
      const name = stat['of']['name'];
      const lat = stat['of']['geo']['lat'];
      const lnt = stat['of']['geo']['lnt'];
      const radius = stat['of']['radius'];

      const type = stat['type'];
      const amount = stat['amount'];

      const color = this.getColor(amount);
      const fillOpacity = 0.7;

      const circle = L.circle([lat, lnt], {
        color: color,
        fillColor: color,
        fillOpacity: fillOpacity,
        radius: radius
      }).addTo(this.map);
      circle.bindPopup('<b>' + name + '</b><br>' + type + ' $' + amount);

      this.statsType = type;
      this.circles.push(circle);
    });
  }

  getColor(d: number): string {
    return d > 3500  ? '#800026' :
           d > 3000  ? '#BD0026' :
           d > 2500  ? '#E31A1C' :
           d > 2000  ? '#FC4E2A' :
           d > 1500  ? '#FD8D3C' :
           d > 1000  ? '#FEB24C' :
           d > 500   ? '#FED976' :
                       '#FFEDA0';
  }

  // // TODO: add info ctrl
  // initInfoCtrl(): void {
  //   const info = L.control({position: 'topleft'});
  //   const mapClass = this;

  //   info.onAdd = function(map) {
  //       this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
  //       this.update();
  //       return this._div;
  //   };

  //   // method that we will use to update the control based on feature properties passed
  //   info.update = function (props) {
  //       this._div.innerHTML = '<h4>' + mapClass.statsType + ' Housing Price</h4>' +  (props ?
  //           '<b>' + props.name + '</b><br />$' + props.amount : 'Hover over a region');
  //   };

  //   this.info = info.addTo(this.map);
  // }

  initLegend(): void {
    const legend = L.control({position: 'topleft'});

    legend.onAdd = map => {

      const div = L.DomUtil.create('div', 'info legend');

      // loop through our density intervals and generate a label with a colored square for each interval
      for (let i = 0; i < this.intervals.length; i++) {
        div.innerHTML +=
          '<i style="background:' + this.getColor(this.intervals[i] + 1) + '"></i> ' +
          this.intervals[i] + (this.intervals[i + 1] ? '&ndash;' + this.intervals[i + 1] + '<br>' : '+');
      }

      return div;
    };

    this.legend = legend.addTo(this.map);
  }

}
