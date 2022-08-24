<script lang="ts">
import { Map, GeoJSONSource } from 'mapbox-gl'
import { toGeoJson } from '../util/util'
import { defineComponent, ref, Ref, defineAsyncComponent, watchEffect } from "vue";
import { MapboxMap, MapboxPopup } from "vue-mapbox-ts";
import { getBreweries, socket } from '../services/api'
import { IBreweryProperties, BreweryFeatureCollection, BreweryFeature } from '../types/types'
import Toast from 'primevue/toast';
import { useToast } from "primevue/usetoast";
console.log('mapbox popup: ', MapboxPopup)
const FeaturePopup = defineAsyncComponent(()=> import('../components/FeaturePopup.vue'))


export default defineComponent({
  name: 'map-view',
  components: {
    Toast,
    MapboxMap,
    MapboxPopup,
    FeaturePopup
  },

  setup(){
    const toast = useToast()
    const map: Ref<Map | undefined> = ref();
    const breweryFeatures: Ref<BreweryFeatureCollection> = ref({
      type: 'FeatureCollection',
      features: []
    } as BreweryFeatureCollection)

    const selectedFeature: Ref<BreweryFeature | undefined> = ref()

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

      const eventsFC = {
          type: "FeatureCollection", 
          features: []
        } as BreweryFeatureCollection

      mb_map.addSource('events-source', {
        type: 'geojson',
        data: eventsFC
      })

      mb_map.addLayer({
        id: 'events',
        type: 'circle',
        source: 'events-source',
        paint: {
          'circle-radius': 9,
          'circle-color': 'red'
        }
      })

      const source = mb_map.getSource('breweries-source') as GeoJSONSource 
      const eventSource = mb_map.getSource('events-source') as GeoJSONSource 

      mb_map.on('click', 'breweries', (e)=> {
        selectedFeature.value = undefined
        const feature = e.features ? e.features[0]: undefined
        if (feature){
          selectedFeature.value = feature as BreweryFeature
          console.log('selected feature: ', selectedFeature.value)
        } else {
          selectedFeature.value = undefined
        }
      })

      console.log('loaded map: ', breweryFeatures.value)
      //@ts-ignore
      window.toast = toast

      socket.on('brewery/create', (payload: IBreweryProperties)=> {
        const ft = toGeoJson(payload)
        breweryFeatures.value.features.push(ft)
        eventsFC.features.push(ft)
        eventSource.setData(eventsFC)
        source.setData(breweryFeatures.value)
        console.log('detected new brewery, zooming now', ft)
        mb_map.flyTo({
          center: ft.geometry.coordinates as [number, number],
          zoom: 16
        })
        toast.add({
          severity: 'success',
          summary: 'New Brewery',
          detail: `detected new brewrey: "${payload.name}" (id: ${payload.id})`,
          life: 30000 
        })

        // clear temporary red symbols
        setTimeout(()=> {
          eventsFC.features = []
          eventSource.setData(eventsFC)
        }, 5000)
      })

      socket.on('brewery/delete', (brewery: IBreweryProperties)=> {
        console.log('brewery delete event', brewery)
        const ft = breweryFeatures.value.features.find(ft => ft.properties.id === brewery.id)
        if (ft){
          const index = breweryFeatures.value.features.indexOf(ft)
          breweryFeatures.value.features.splice(index, 1)
          console.log('removed feature from map: ', ft)
          source.setData(breweryFeatures.value)
          toast.add({
            severity: 'error',
            summary: 'Deleted Brewery',
            detail: `brewerey removed: "${brewery.name}" (id: ${brewery.id})`,
            life: 30000 
          })
        }
      })

      socket.on('brewery/patch', (brewery: IBreweryProperties)=> {
        console.log('brewery patch event', brewery)
        const ft = breweryFeatures.value.features.find(ft => ft.properties.id === brewery.id)
        if (ft){
          const index = breweryFeatures.value.features.indexOf(ft)
          breweryFeatures.value.features.splice(index, 1)
          console.log('removed feature from map: ', ft)
          const updatedFt = toGeoJson(brewery)
          breweryFeatures.value.features.push(updatedFt)
          source.setData(breweryFeatures.value)
          toast.add({
            severity: 'warn',
            summary: 'Updated Brewery',
            detail: `brewrey updated: "${brewery.name}" (id: ${brewery.id})\n${JSON.stringify(brewery, null, 2)}`,
            life: 30000 
          })
        }
      })
    }
  
    return {
      map,
      breweryFeatures,
      selectedFeature,
      onMapLoaded,
      accessToken: import.meta.env.VITE_MAPBOX_TOKEN
    }
  },

  mounted(){
    watchEffect(()=> {
        if (this.$refs.popup){
          console.log('popup ref is: ', this.$refs.popup)
          if (this.selectedFeature){
            (this.$refs.popup as typeof MapboxPopup).open()
          }
        }
      })
  }
  
})

</script>

<template>

<div class="map-view-container">
  <Toast :position="'top-right'" />
  <mapbox-map
    :center="[-93.5, 44,5]"
    :zoom="8"
    :accessToken="accessToken"
    mapStyle="streets-v11"
    @loaded="onMapLoaded"
  >
    <mapbox-popup 
      v-if="selectedFeature"
      ref="popup" 
      :lngLat="selectedFeature?.geometry?.coordinates"
      @close="()=> selectedFeature = undefined"
    >
      <div>
        <p><strong>{{ selectedFeature?.properties.name }}</strong></p>
        <feature-popup 
          :feature="selectedFeature!"
          :fields="['id', 'address', 'city']"
        ></feature-popup>
      </div>
    </mapbox-popup>

  </mapbox-map>
</div>

</template>

<style>
  .map-view-container {
    height: 700px;
    width: 100%;
  }
</style>