/**
 * ==========================================================
 * MH CLUB - NEXT-LEVEL ANIMATED & STATISTICAL ADMIN DASHBOARD
 * ==========================================================
 */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        initStatCounters();
        initLiveClock();
        initDashboardCharts();
    });

    /**
     * ======================================================
     * 1. SMOOTH ANIMATED NUMBER COUNTERS (ROLL-UP EFFECT)
     * ======================================================
     */
    function initStatCounters() {
        const counters = document.querySelectorAll(".stat-counter");
        if (!counters.length) return;

        counters.forEach(counter => {
            const targetVal = parseFloat(counter.getAttribute("data-target")) || 0;
            const prefix = counter.getAttribute("data-prefix") || "";
            const decimals = parseInt(counter.getAttribute("data-decimals"), 10) || 0;
            const duration = 1200; // ms
            const startTime = performance.now();

            function updateCounter(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Ease out expo formula for premium feel
                const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                const currentVal = targetVal * easeProgress;

                let formatted = "";
                if (decimals > 0) {
                    formatted = currentVal.toLocaleString("en-IN", {
                        minimumFractionDigits: decimals,
                        maximumFractionDigits: decimals
                    });
                } else {
                    formatted = Math.round(currentVal).toLocaleString("en-IN");
                }

                counter.textContent = prefix + formatted;

                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                } else {
                    if (decimals > 0) {
                        counter.textContent = prefix + targetVal.toLocaleString("en-IN", {
                            minimumFractionDigits: decimals,
                            maximumFractionDigits: decimals
                        });
                    } else {
                        counter.textContent = prefix + Math.round(targetVal).toLocaleString("en-IN");
                    }
                }
            }

            requestAnimationFrame(updateCounter);
        });
    }

    /**
     * ======================================================
     * 2. REAL-TIME CLOCK IN HEADER
     * ======================================================
     */
    function initLiveClock() {
        const clockEl = document.getElementById("dashboard-live-clock");
        if (!clockEl) return;

        function updateTime() {
            const now = new Date();
            const options = { 
                weekday: 'short', 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                hour12: true 
            };
            clockEl.textContent = now.toLocaleDateString('en-US', options);
        }

        updateTime();
        setInterval(updateTime, 1000);
    }

    /**
     * ======================================================
     * 3. APEXCHARTS ENGINE (STATISTICAL VISUALIZATIONS)
     * ======================================================
     */
    function initDashboardCharts() {
        const dataEl = document.getElementById("dashboard-chart-data");
        if (!dataEl || typeof ApexCharts === "undefined") {
            return;
        }

        let chartData = {};
        try {
            chartData = JSON.parse(dataEl.textContent);
        } catch (e) {
            console.error("Failed to parse dashboard chart data JSON", e);
            return;
        }

        const isDark = document.documentElement.classList.contains("dark") || 
                       document.body.classList.contains("dark");

        const chartThemeMode = isDark ? "dark" : "light";
        const gridBorderColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";
        const textMutedColor = isDark ? "#94a3b8" : "#64748b";

        // --------------------------------------------------
        // CHART 1: REVENUE & ORDERS AREA CHART
        // --------------------------------------------------
        const revContainer = document.querySelector("#chart-revenue-growth");
        if (revContainer) {
            const revOptions = {
                series: [
                    {
                        name: "Revenue (₹)",
                        data: chartData.timeline7Revenue || [0]
                    },
                    {
                        name: "Order Count",
                        data: chartData.timeline7Orders || [0]
                    }
                ],
                chart: {
                    type: "area",
                    height: 320,
                    toolbar: { show: false },
                    fontFamily: "Outfit, Inter, sans-serif",
                    background: "transparent",
                    animations: {
                        enabled: true,
                        easing: "easeinout",
                        speed: 800
                    }
                },
                colors: ["#6366f1", "#10b981"],
                dataLabels: { enabled: false },
                stroke: {
                    curve: "smooth",
                    width: [3, 2]
                },
                fill: {
                    type: "gradient",
                    gradient: {
                        shadeIntensity: 1,
                        opacityFrom: 0.45,
                        opacityTo: 0.05,
                        stops: [0, 95, 100]
                    }
                },
                xaxis: {
                    categories: chartData.timeline7Labels || [],
                    labels: {
                        style: { colors: textMutedColor, fontSize: "12px", fontWeight: 500 }
                    },
                    axisBorder: { show: false },
                    axisTicks: { show: false }
                },
                yaxis: [
                    {
                        title: { text: "Revenue", style: { color: "#6366f1", fontWeight: 600 } },
                        labels: {
                            formatter: val => "₹" + Math.round(val).toLocaleString("en-IN"),
                            style: { colors: textMutedColor, fontSize: "11px" }
                        }
                    },
                    {
                        opposite: true,
                        title: { text: "Orders", style: { color: "#10b981", fontWeight: 600 } },
                        labels: {
                            formatter: val => Math.round(val),
                            style: { colors: textMutedColor, fontSize: "11px" }
                        }
                    }
                ],
                grid: {
                    borderColor: gridBorderColor,
                    strokeDashArray: 4
                },
                theme: { mode: chartThemeMode },
                tooltip: {
                    theme: chartThemeMode,
                    shared: true,
                    intersect: false,
                    y: {
                        formatter: (val, opts) => {
                            if (opts.seriesIndex === 0) {
                                return "₹" + Number(val).toLocaleString("en-IN");
                            }
                            return val + " orders";
                        }
                    }
                },
                legend: {
                    position: "top",
                    horizontalAlign: "right",
                    labels: { colors: textMutedColor }
                }
            };

            const revChart = new ApexCharts(revContainer, revOptions);
            revChart.render();

            // Period Switcher Buttons (7D vs 30D)
            const btn7d = document.getElementById("btn-chart-7d");
            const btn30d = document.getElementById("btn-chart-30d");

            if (btn7d && btn30d) {
                btn7d.addEventListener("click", function () {
                    btn7d.className = "chart-period-btn-active";
                    btn30d.className = "chart-period-btn-inactive";
                    
                    revChart.updateOptions({
                        xaxis: { categories: chartData.timeline7Labels || [] }
                    });
                    revChart.updateSeries([
                        { name: "Revenue (₹)", data: chartData.timeline7Revenue || [0] },
                        { name: "Order Count", data: chartData.timeline7Orders || [0] }
                    ]);
                });

                btn30d.addEventListener("click", function () {
                    btn30d.className = "chart-period-btn-active";
                    btn7d.className = "chart-period-btn-inactive";
                    
                    revChart.updateOptions({
                        xaxis: { categories: chartData.timeline30Labels || [] }
                    });
                    revChart.updateSeries([
                        { name: "Revenue (₹)", data: chartData.timeline30Revenue || [0] },
                        { name: "Order Count", data: chartData.timeline30Orders || [0] }
                    ]);
                });
            }
        }

        // --------------------------------------------------
        // CHART 2: ORDER STATUS DONUT CHART
        // --------------------------------------------------
        const statusContainer = document.querySelector("#chart-order-status");
        if (statusContainer) {
            const statusSeries = (chartData.orderStatusSeries && chartData.orderStatusSeries.some(v => v > 0))
                ? chartData.orderStatusSeries
                : [1, 0, 0, 0];

            const statusOptions = {
                series: statusSeries,
                labels: chartData.orderStatusLabels || ["Paid", "Pending", "Cancelled", "Returned"],
                chart: {
                    type: "donut",
                    height: 270,
                    fontFamily: "Outfit, Inter, sans-serif",
                    background: "transparent",
                    animations: { enabled: true, speed: 900 }
                },
                colors: ["#10b981", "#f59e0b", "#f43f5e", "#a855f7"],
                stroke: { width: 0 },
                plotOptions: {
                    pie: {
                        donut: {
                            size: "72%",
                            labels: {
                                show: true,
                                name: { show: true, fontSize: "12px", color: textMutedColor },
                                value: {
                                    show: true,
                                    fontSize: "20px",
                                    fontWeight: "800",
                                    color: isDark ? "#ffffff" : "#1e293b",
                                    formatter: val => val
                                },
                                total: {
                                    show: true,
                                    label: "Total Orders",
                                    fontSize: "11px",
                                    color: textMutedColor,
                                    formatter: w => {
                                        return w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                                    }
                                }
                            }
                        }
                    }
                },
                dataLabels: { enabled: false },
                legend: { show: false },
                tooltip: { theme: chartThemeMode }
            };

            const statusChart = new ApexCharts(statusContainer, statusOptions);
            statusChart.render();
        }

        // --------------------------------------------------
        // CHART 3: CATEGORY BAR CHART
        // --------------------------------------------------
        const catContainer = document.querySelector("#chart-category-bar");
        if (catContainer) {
            const catLabels = (chartData.categoriesLabels && chartData.categoriesLabels.length)
                ? chartData.categoriesLabels
                : ["General", "Accessories", "Footwear"];
            const catSeries = (chartData.categoriesSeries && chartData.categoriesSeries.length)
                ? chartData.categoriesSeries
                : [3, 2, 1];

            const catOptions = {
                series: [{ name: "Products", data: catSeries }],
                chart: {
                    type: "bar",
                    height: 240,
                    toolbar: { show: false },
                    fontFamily: "Outfit, Inter, sans-serif",
                    background: "transparent"
                },
                plotOptions: {
                    bar: {
                        borderRadius: 8,
                        columnWidth: "45%",
                        distributed: true
                    }
                },
                colors: ["#6366f1", "#8b5cf6", "#ec4899", "#3b82f6", "#10b981", "#f59e0b"],
                dataLabels: {
                    enabled: true,
                    style: { fontSize: "11px", fontWeight: "bold" },
                    offsetY: -18
                },
                xaxis: {
                    categories: catLabels,
                    labels: { style: { colors: textMutedColor, fontSize: "11px" } },
                    axisBorder: { show: false },
                    axisTicks: { show: false }
                },
                yaxis: {
                    labels: { style: { colors: textMutedColor, fontSize: "11px" } }
                },
                grid: { borderColor: gridBorderColor, strokeDashArray: 4 },
                legend: { show: false },
                tooltip: { theme: chartThemeMode }
            };

            const catChart = new ApexCharts(catContainer, catOptions);
            catChart.render();
        }

        // --------------------------------------------------
        // CHART 4: PAYMENT DISTRIBUTION DONUT
        // --------------------------------------------------
        const payContainer = document.querySelector("#chart-payment-donut");
        if (payContainer) {
            const paySeries = (chartData.paymentSeries && chartData.paymentSeries.some(v => v > 0))
                ? chartData.paymentSeries
                : [10, 11];

            const payOptions = {
                series: paySeries,
                labels: chartData.paymentLabels || ["Online (Razorpay)", "Cash on Delivery"],
                chart: {
                    type: "donut",
                    height: 240,
                    fontFamily: "Outfit, Inter, sans-serif",
                    background: "transparent"
                },
                colors: ["#06b6d4", "#6366f1"],
                stroke: { width: 0 },
                plotOptions: {
                    pie: {
                        donut: {
                            size: "70%",
                            labels: {
                                show: true,
                                name: { show: true, fontSize: "12px", color: textMutedColor },
                                value: {
                                    show: true,
                                    fontSize: "18px",
                                    fontWeight: "800",
                                    color: isDark ? "#ffffff" : "#1e293b"
                                },
                                total: {
                                    show: true,
                                    label: "Transactions",
                                    color: textMutedColor,
                                    fontSize: "11px"
                                }
                            }
                        }
                    }
                },
                dataLabels: { enabled: false },
                legend: {
                    position: "bottom",
                    labels: { colors: textMutedColor }
                },
                tooltip: { theme: chartThemeMode }
            };

            const payChart = new ApexCharts(payContainer, payOptions);
            payChart.render();
        }
    }

})();
