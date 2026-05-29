import { useSyncExternalStore } from 'react';

type Listener = () => void;
type SetState<T> = (partial: Partial<T> | ((state: T) => Partial<T>)) => void;
type GetState<T> = () => T;
type StoreHook<T> = {
  <U>(selector: (state: T) => U): U;
  getState: GetState<T>;
  setState: SetState<T>;
  subscribe: (listener: Listener) => () => void;
};

export function create<T>(initializer: (set: SetState<T>, get: GetState<T>) => T): StoreHook<T> {
  let state: T;
  const listeners = new Set<Listener>();
  const getState = () => state;
  const setState: SetState<T> = (partial) => {
    const patch = typeof partial === 'function' ? partial(state) : partial;
    state = { ...state, ...patch };
    listeners.forEach((listener) => listener());
  };
  const subscribe = (listener: Listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };
  state = initializer(setState, getState);
  function useStore<U>(selector: (state: T) => U): U {
    return useSyncExternalStore(subscribe, () => selector(state), () => selector(state));
  }
  useStore.getState = getState;
  useStore.setState = setState;
  useStore.subscribe = subscribe;
  return useStore;
}
