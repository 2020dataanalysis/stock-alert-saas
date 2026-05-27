/*
|--------------------------------------------------------------------------
| File: chart.js
|--------------------------------------------------------------------------
| SVG price chart rendering, cursor movement, and alert markers.
|--------------------------------------------------------------------------
*/

function buildChartScales(data) {
    const width = 1000;
    const height = 300;
    const padding = 20;

    const prices = data.map(function(point) {
        return point.price;
    });

    const minPrice = Math.min.apply(null, prices);
    const maxPrice = Math.max.apply(null, prices);
    const priceRange = maxPrice - minPrice || 1;

    function xScale(index) {
        if (data.length === 1) {
            return padding;
        }

        return padding +
            (index / (data.length - 1)) *
            (width - padding * 2);
    }

    function yScale(price) {
        return height - padding -
            ((price - minPrice) / priceRange) *
            (height - padding * 2);
    }

    return {
        width: width,
        height: height,
        padding: padding,
        xScale: xScale,
        yScale: yScale
    };
}

function drawShockMarkers(svg, data, scales) {
    if (!showShockMarkers) {
        return;
    }

    data.forEach(function(point) {
        if (point.shock < 1.0) {
            return;
        }

        const marker = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "circle"
        );

        marker.setAttribute("cx", scales.xScale(point.index));
        marker.setAttribute("cy", scales.yScale(point.price));
        marker.setAttribute("r", Math.min(3 + point.shock, 12));
        marker.setAttribute("class", "shock-marker");
        marker.setAttribute("data-shock", point.shock.toFixed(2));

        svg.appendChild(marker);
    });
}

function drawStateChangeMarkers(svg, data, scales) {
    if (!showStateMarkers) {
        return;
    }

    for (let i = 1; i < data.length; i += 1) {
        const previous = data[i - 1];
        const current = data[i];

        if (previous.state === current.state) {
            continue;
        }

        const x = scales.xScale(current.index);
        const y = scales.yScale(current.price);

        const marker = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "rect"
        );

        marker.setAttribute("x", x - 5);
        marker.setAttribute("y", y - 5);
        marker.setAttribute("width", 10);
        marker.setAttribute("height", 10);
        marker.setAttribute("class", "state-marker");
        marker.setAttribute(
            "data-state-change",
            previous.state + " -> " + current.state
        );

        svg.appendChild(marker);
    }
}

function drawPermissionMarkers(svg, data, scales) {
    if (!showPermissionMarkers) {
        return;
    }

    for (let i = 1; i < data.length; i += 1) {
        const previous = data[i - 1];
        const current = data[i];

        if (previous.permission === current.permission) {
            continue;
        }

        const x = scales.xScale(current.index);

        const marker = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "line"
        );

        marker.setAttribute("x1", x);
        marker.setAttribute("x2", x);
        marker.setAttribute("y1", scales.padding);
        marker.setAttribute("y2", scales.height - scales.padding);
        marker.setAttribute("class", "permission-marker");
        marker.setAttribute(
            "data-permission-change",
            previous.permission + " -> " + current.permission
        );

        svg.appendChild(marker);
    }
}

function drawPriceChart() {
    const svg = document.getElementById("price-chart");
    const data = getChartData();

    if (!svg || data.length === 0) {
        return;
    }

    svg.innerHTML = "";

    const scales = buildChartScales(data);

    const points = data.map(function(point) {
        return (
            scales.xScale(point.index) + "," +
            scales.yScale(point.price)
        );
    }).join(" ");

    const polyline = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "polyline"
    );

    polyline.setAttribute("points", points);
    polyline.setAttribute("class", "price-line");

    svg.appendChild(polyline);

    drawShockMarkers(svg, data, scales);
    drawStateChangeMarkers(svg, data, scales);
    drawPermissionMarkers(svg, data, scales);

    const cursorLine = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "line"
    );

    cursorLine.setAttribute("id", "price-cursor-line");
    cursorLine.setAttribute("class", "price-cursor");
    cursorLine.setAttribute("y1", scales.padding);
    cursorLine.setAttribute("y2", scales.height - scales.padding);

    svg.appendChild(cursorLine);

    const cursorDot = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "circle"
    );

    cursorDot.setAttribute("id", "price-cursor-dot");
    cursorDot.setAttribute("class", "price-dot");
    cursorDot.setAttribute("r", 5);

    svg.appendChild(cursorDot);

    updateChartCursor();
}

function updateChartCursor() {
    const data = getChartData();

    if (data.length === 0) {
        return;
    }

    const scales = buildChartScales(data);

    const index = liveDataBuffer.length > 0
        ? data.length - 1
        : currentIndex;

    const point = data[index];

    const x = scales.xScale(point.index);
    const y = scales.yScale(point.price);

    const cursorLine = document.getElementById(
        "price-cursor-line"
    );

    const cursorDot = document.getElementById(
        "price-cursor-dot"
    );

    if (cursorLine) {
        cursorLine.setAttribute("x1", x);
        cursorLine.setAttribute("x2", x);
    }

    if (cursorDot) {
        cursorDot.setAttribute("cx", x);
        cursorDot.setAttribute("cy", y);
    }
}
