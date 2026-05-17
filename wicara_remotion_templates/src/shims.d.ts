declare namespace React {
  type ReactNode = any;
  type FC<P = any> = any;
}

declare module "react" {
  export type CSSProperties = any;
  export type ReactNode = any;
  const React: any;
  export default React;
  export const Fragment: any;
}

declare module "react/jsx-runtime" {
  export const jsx: any;
  export const jsxs: any;
  export const Fragment: any;
}

declare module "remotion" {
  export const AbsoluteFill: any;
  export const Composition: any;
  export const registerRoot: any;
  export const interpolate: any;
  export const spring: any;
  export const useCurrentFrame: any;
  export const useVideoConfig: any;
}

declare namespace JSX {
  interface IntrinsicElements { [elemName: string]: any; }
}
