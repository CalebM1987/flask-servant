<script lang="ts">
import { Map } from 'mapbox-gl'
import { toGeoJson } from '../util/util'
import { FeatureCollection, Point } from 'geojson'
import { defineComponent, ref, Ref, watch, watchEffect } from "vue";
import { MapboxMap } from "vue-mapbox-ts";
import { getBreweries, socket } from '../services/api'
import { IBreweryProperties, BreweryFeatureCollection } from '../types/types'

export default defineComponent({
  name: 'map-view',
  components: {
    MapboxMap,
  },

  setup(){

    const map: Ref<Map | undefined> = ref();
    const breweryFeatures: Ref<BreweryFeatureCollection> = ref({
      type: 'FeatureCollection',
      features: []
    } as BreweryFeatureCollection)

    const onMapLoaded = async (mb_map: Map) => {
      map.value = mb_map

      const { features } = await getBreweries()
      console.log('loaded brewery features: ', breweryFeatures)
      breweryFeatures.value.features = features

      mb_map.addSource('breweries-source', {
        type: 'geojson',
        data: breweryFeatures.value
      })

      mb_map.addLayer({
        id: 'breweries',
        type: 'circle',
        source: 'breweries-source',
        paint: {
          'circle-radius': 8,
          'circle-color': 'blue'
        }
      })

      console.log('loaded map: ', breweryFeatures.value)

      socket.on('brewery/create', (payload: IBreweryProperties)=> {
        const ft = toGeoJson(payload)
        breweryFeatures.value.features.push(ft)
        console.log('detected new brewery, zooming now', ft)
        mb_map.flyTo({
          center: ft.geometry.coordinates as [number, number],
          zoom: 17
        })
      })

      socket.on('brewery/delete', (brewery: IBreweryProperties)=> {
        console.log('brewery delete event', brewery)
        const ft = breweryFeatures.value.features.find(ft => ft.properties.id === brewery.id)
        if (ft){
          const index = breweryFeatures.value.features.indexOf(ft)
          breweryFeatures.value.features.splice(index, 1)
          console.log('removed feature from map: ', ft)
        }
      })
    }
  
    return {
      map,
      breweryFeatures,
      onMapLoaded,
      accessToken: import.meta.env.VITE_MAPBOX_TOKEN
    }
  }
  
})

</script>

<template>

<div class="map-container">
  <mapbox-map
    :center="[-93.5, 44,5]"
    :zoom="8"
    :accessToken="accessToken"
    mapStyle="streets-v11"
    @loaded="onMapLoaded"
  >

  </mapbox-map>
</div>

</template>

<style>
  .map-container {
    height: calc(90vh);
    width: 100%;
  }
</style>