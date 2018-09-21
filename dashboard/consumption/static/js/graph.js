import HyperHTMLElement from "hyperhtml-element/esm";
import echart from "echarts";

class XGraph extends HyperHTMLElement {
  created() {
    this.render();
  }

  render() {
    return this.html`<div id="graph"></div>`;
  }

  plotData(consumptionData) {
    this.firstElementChild.style.width = `${this.getAttribute("width")}px`;
    this.firstElementChild.style.height = `${this.getAttribute("height")}px`;
    this.graph = echart.init(this.firstElementChild);
    this.boundaryGap = true;
    this.labelGap = 35;
    if (this.getAttribute("type") === "line") {
      this.boundaryGap = false;
    } else if (this.getAttribute("type") === "bar") {
      this.labelGap = 55;
    }
    this.graph.setOption({
      title: {
        text: this.getAttribute("title"),
        left: "center",
      },
      tooltip: {},
      legend: {
        data: [],
      },
      xAxis: {
        name: this.getAttribute("x_axis"),
        data: consumptionData.x_axis,
        nameLocation: "middle",
        boundaryGap: this.boundaryGap,
        nameGap: 40,
      },
      yAxis: {
        name: this.getAttribute("y_axis"),
        nameLocation: "middle",
        nameGap: this.labelGap,
      },
      series: [
        {
          type: this.getAttribute("type"),
          data: consumptionData.y_axis,
        },
        {
          type: "custom",
          itemStyle: {
            normal: {
              borderWidth: 1.5,
            },
          },
          renderItem(_, api) {
            const xValue = api.value(0);
            const highPoint = api.coord([
              xValue,
              api.value(1) + consumptionData.sem[xValue],
            ]);
            const lowPoint = api.coord([
              xValue,
              api.value(1) - consumptionData.sem[xValue],
            ]);
            const halfWidth = api.size([1, 0])[0] * 0.05;
            const style = api.style({
              stroke: api.visual("color"),
              fill: null,
            });

            return {
              type: "group",
              children: [
                {
                  type: "line",
                  shape: {
                    x1: highPoint[0] - halfWidth,
                    y1: highPoint[1],
                    x2: highPoint[0] + halfWidth,
                    y2: highPoint[1],
                  },
                  style,
                },
                {
                  type: "line",
                  shape: {
                    x1: highPoint[0],
                    y1: highPoint[1],
                    x2: lowPoint[0],
                    y2: lowPoint[1],
                  },
                  style,
                },
                {
                  type: "line",
                  shape: {
                    x1: lowPoint[0] - halfWidth,
                    y1: lowPoint[1],
                    x2: lowPoint[0] + halfWidth,
                    y2: lowPoint[1],
                  },
                  style,
                },
              ],
            };
          },
          encode: {
            x: 0,
            y: [1, 2],
          },
          data: consumptionData.y_axis,
          z: 100,
        },
      ],
      dataZoom: [
        {
          type: "slider",
          height: 4,
          bottom: 30,
          borderColor: "transparent",
          backgroundColor: "#e2e2e2",
          handleIcon:
            "M10.7,11.9H9.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4h1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7v-1.2h6.6z M13.3,22H6.7v-1.2h6.6z M13.3,19.6H6.7v-1.2h6.6z", // jshint ignore:line
          handleSize: 10,
          handleStyle: {
            shadowBlur: 6,
            shadowOffsetX: 1,
            shadowOffsetY: 2,
            shadowColor: "#aaa",
          },
        },
        {
          type: "inside",
        },
      ],
    });
  }

  async connectedCallback() {
    this.firstElementChild.style.width = `${this.getAttribute("width")}px`;
    this.firstElementChild.style.height = `${this.getAttribute("height")}px`;
    this.graph = echart.init(this.firstElementChild);
  }
}

XGraph.define("x-graph");