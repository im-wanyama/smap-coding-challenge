import "document-register-element";
import "./graph";
import { getConsumptionData } from "./api";

getConsumptionData(3000).then(data => {
  const xgraphs = [...document.querySelectorAll("x-graph")];
  const graphData = data;
  for (let index = 0; index < xgraphs.length; index++) {
    xgraphs[index].plotData(graphData[index]);
  }
});
