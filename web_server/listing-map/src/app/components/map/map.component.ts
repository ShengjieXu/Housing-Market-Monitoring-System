import { Component, OnInit } from '@angular/core';

import { Statistics, Listings } from '../../models/data.model';
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
  resetBtn: any;
  legend: any;
  info: any;
  regions: any;
  circles = [];
  markers = [];
  fillOpacity = 0.7;

  intervals: number[] = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500];

  statsType = 'Average';
  statistics: Statistics;

  listings: Listings;

  constructor(private ds: DataService) { }

  ngOnInit() {
    this.loadMap();
    this.loadRegions();
  }

  resetMap(): void {
    const lat = this.defaultView['geo']['lat'];
    const lnt = this.defaultView['geo']['lnt'];
    const zoomLevel = this.defaultView['zoomLevel'];

    if (this.map != null) {
      this.map.setView([lat, lnt], zoomLevel);
    } else {
      this.map = L.map('map').setView([lat, lnt], zoomLevel);
    }
  }

  refillCircles(): void {
    this.circles.forEach(circle => {
      circle.setStyle({fillOpacity: this.fillOpacity});
    });
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

    this.initResetBtn();
    this.initLegend();
    this.initLoadingCtrl();
  }

  initResetBtn(): void {
    L.easyButton('<span class="star">&starf;</span>', (btn, map) => {
      this.resetMap();
      this.refillCircles();
      this.resetMarkers();
    }).addTo(this.map);
  }

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

  initLoadingCtrl(): void {
    const loadingControl = L.Control.loading({
      separate: true
    });
    this.map.addControl(loadingControl);
  }

  loadRegions(): void {
    this.ds.getRegions()
      .subscribe(regions => {
        this.regions = regions;
        // stats is dependent on regions, so load stats after regions are loaded
        this.loadStats();
      });
  }

  loadStats(): void {
    this.map.fire('dataloading');
    this.ds.getStatistics()
      .subscribe(statistics => {
        this.statistics = statistics;
        this.visualizeStats();
        this.map.fire('dataload');
      });
  }

  loadListings(region: string): void {
    this.map.fire('dataloading');
    this.ds.getListings(region)
      .subscribe(listings => {
        this.listings = listings;
        this.visualizeListings();
        this.map.fire('dataload');
      });
  }

  resetMarkers(): void {
    // remove existing markers
    this.markers.forEach(marker => {
      marker.remove();
    });
    this.markers = [];
  }

  visualizeListings(): void {
    this.resetMarkers();

    const region = this.listings['region'];

    if (this.listings != null && this.listings['payloads'].length > 0) {
      const myIcon = L.icon({
        iconUrl: 'assets/icon_place.svg',
        iconSize: [38, 95],
        iconAnchor: [22, 94],
        popupAnchor: [-3, -76],
      });

      this.listings['payloads'].forEach(payload => {

        const url =  payload['url'],
              title = payload['title'],
              price = payload['price'],
              geo = payload['geo'],
              lat = geo['latitude'],
              lnt = geo['longitude'],
              bed = payload['bed'],
              bath = payload['bath'],
              available_date = payload['available_date'],
              img_url = payload['img_url'];

        if (lat != null && lnt != null) {
          const marker = L.marker([lat, lnt], {icon: myIcon}).addTo(this.map);

          marker.bindPopup('<b><a href="' + url + '">' + title + '</a></b><br>' +
            'price:' + price + '<br>' +
            'bed: ' + bed + '<br>' +
            'bath: ' + bath + '<br>' +
            'available date: ' + available_date + '<br>' +
            '<img src="' + img_url + '" class="thumbnail">'
          );

          this.markers.push(marker);
        }
      });

    }
  }

  resetCircles(): void {
    // remove existing circles
    this.circles.forEach(circle => {
      circle.remove();
    });
    this.circles = [];
  }

  visualizeStats(): void {
    const mapClass = this;

    this.resetCircles();

    const type = this.statistics['type'];
    this.statsType = type;

    // draw new circles
    if (this.statistics != null && this.statistics['payloads'].length > 0) {
      this.statistics['payloads'].forEach(payload => {
        const region = payload['region'];
        const count = payload['count'];
        const data = payload['data'];

        if (this.regions != null && this.regions.hasOwnProperty(region)) {
          const lat = this.regions[region]['geo']['lat'];
          const lnt = this.regions[region]['geo']['lnt'];
          const radius = this.regions[region]['radius'];

          const color = this.getColor(data);

          const circle = L.circle([lat, lnt], {
            color: color,
            fillColor: color,
            fillOpacity: mapClass.fillOpacity,
            radius: radius
          }).addTo(this.map);
          circle.bindTooltip('<b>' + region.toLocaleUpperCase() + '</b><br>' +
            type + ' $' + data.toFixed(0) + '<br>' +
            'from recent ' + count.toFixed(0) + ' data', {
              direction: 'top'
            }
          );

          circle.on('click', function(e) {
            mapClass.map.setZoomAround([lat, lnt], 10);
            // clear tooltip and fill
            this.closeTooltip();
            this.setStyle({fillOpacity: 0});

            // get listings and display
            mapClass.loadListings(region);
          });

          this.circles.push(circle);
        }
      });
    }
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

}
