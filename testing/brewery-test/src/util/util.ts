import { Socket } from 'socket.io-client'
import { ISocketEvent, SocketOperation, IBreweryProperties } from '../types/types';
import { FeatureCollection, Point, Feature } from 'geojson'

export function toGeoJson(brewery: IBreweryProperties): Feature<Point, IBreweryProperties> {
  return {
    type: 'Feature',
    properties: brewery,
    geometry: {
      type: 'Point',
      coordinates: [ brewery.longitude!, brewery.latitude! ]
    }
  }
}

export function handleSocket(socket: Socket, eventName: string, payload: any): ISocketEvent {
  const [name, type] = eventName.split('/') as [string, SocketOperation]
  
  let theme: string | undefined;

  switch (type) {
    case 'create':
      theme = 'success';
      break;
    case 'put':
    case 'patch':
      theme = 'warning';
      break;
    case 'delete':
      theme = 'danger';
      break;
    default:
      theme = undefined;
  }
  
  
  return {
    name,
    type,
    payload,
    theme,
    time: new Date().toISOString(),
  }
}