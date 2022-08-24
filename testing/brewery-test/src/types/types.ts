import { Feature, FeatureCollection, Point } from 'geojson'
export type SocketOperation = "find" | "create" | "patch" | "put" | "delete";

export interface ISocketEvent {
  /** the event name */
  name: string;
  /** the type of operation */
  type: SocketOperation;
  /** theme */
  theme?: string;
  /** the event time */
  time: string;
  /** the event payload */
  payload: Record<string, any>;
}

export interface IBreweryProperties {
  id?: number;
  name?: string;
  address?: string;
  city?: string
  state?: string
  zip?: string
  monday?: string
  tuesday?: string;
  wednesday?: string;
  thursday?: string;
  friday?: string;
  saturday?: string;
  sunday?: string;
  comments?: string;
  brew_type?: string;
  website?: string;
  longitude?: number;
  latitude?: number;
  created_by?: number;
  creator?: number;
}

export type BreweryFeature = Feature<Point, IBreweryProperties>;

export type BreweryFeatureCollection = FeatureCollection<Point, IBreweryProperties>;