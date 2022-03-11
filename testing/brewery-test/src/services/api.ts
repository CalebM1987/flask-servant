import axios from 'axios'
import { ref } from 'vue'
import { io } from 'socket.io-client'
import { FeatureCollection, Point } from 'geojson'
import { IBreweryProperties } from '../types/types'
import { toGeoJson } from '../util/util'

export const base_url = ref(`http://${import.meta.env.VITE_FLASK_HOST}/breweries`)

export const socket = io(`ws://${import.meta.env.VITE_FLASK_HOST}`)

export async function getBreweries(params: any={}): Promise<FeatureCollection<Point, IBreweryProperties>> {
  const response = await axios.get(`${base_url.value}/brewery`, { params })
  return {
    type: 'FeatureCollection',
    features: response.data.results.map(toGeoJson)
  }
}
