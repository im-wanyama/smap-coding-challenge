import "document-register-element";
import "./graph";
import { getConsumptionData } from "./api";

const userID = document.getElementsByTagName("x-graph")[0].getAttribute("id");

getConsumptionData(userID).then(data => {
  const xgraphs = [...document.querySelectorAll("x-graph")];
  const graphData = data;
  for (let index = 0; index < xgraphs.length; index++) {
    xgraphs[index].plotData(graphData[index]);
  }
});
