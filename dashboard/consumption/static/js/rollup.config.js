import resolve from "rollup-plugin-node-resolve";
import commonjs from "rollup-plugin-commonjs";
import json from "rollup-plugin-json";
import { terser } from "rollup-plugin-terser";

export default {
  input: "app.js",
  output: {
    file: "bundle.js",
    format: "iife",
  },
  plugins: [
    terser(),
    json(),
    resolve({
      jsnext: true,
      main: true,
      browser: true,
      preferBuiltins: false,
    }),
    commonjs(),
  ],
};
