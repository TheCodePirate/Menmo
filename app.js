const metricsByRange = {
  week: [
    {
      id: 'revenue-realized',
      label: 'Revenue Realized',
      value: '$4.2M',
      change: '+6.4%',
      direction: 'positive',
      description: 'Closed-won ARR captured this week across managed cohorts.',
      sparkline: [2.6, 3.1, 3.4, 3.6, 3.9, 4.1, 4.2],
    },
    {
      id: 'onboarded',
      label: 'Accounts Activated',
      value: '48',
      change: '+12',
      direction: 'positive',
      description: 'Customers achieving time-to-value under 14 days.',
      sparkline: [21, 25, 28, 32, 38, 45, 48],
    },
    {
      id: 'retention',
      label: 'Retention Health',
      value: '97.2%',
      change: '+1.8 pts',
      direction: 'positive',
      description: 'Logo retention of strategic customers on proactive playbooks.',
      sparkline: [91, 92, 93, 94, 95, 96, 97.2],
    },
    {
      id: 'nps',
      label: 'Experience NPS',
      value: '71',
      change: '+4',
      direction: 'positive',
      description: 'Post-orchestration satisfaction for concierge journeys.',
      sparkline: [60, 61, 63, 64, 66, 68, 71],
    },
  ],
  month: [
    {
      id: 'revenue-realized',
      label: 'Revenue Realized',
      value: '$17.6M',
      change: '+12.3%',
      direction: 'positive',
      description: 'Closed ARR vs. plan across enterprise and growth segments.',
      sparkline: [11.8, 12.3, 13.4, 14.1, 15.2, 16.5, 17.6],
    },
    {
      id: 'onboarded',
      label: 'Accounts Activated',
      value: '164',
      change: '+23',
      direction: 'positive',
      description: 'Net-new customers completing guided activation journeys.',
      sparkline: [84, 102, 117, 131, 142, 155, 164],
    },
    {
      id: 'retention',
      label: 'Retention Health',
      value: '95.9%',
      change: '+0.6 pts',
      direction: 'positive',
      description: 'Expansions secured through success planning and coverage.',
      sparkline: [94.2, 94.6, 94.9, 95.1, 95.3, 95.6, 95.9],
    },
    {
      id: 'nps',
      label: 'Experience NPS',
      value: '68',
      change: '+6',
      direction: 'positive',
      description: 'Pulse of orchestrated engagements across the customer lifecycle.',
      sparkline: [54, 56, 58, 60, 63, 65, 68],
    },
  ],
  quarter: [
    {
      id: 'revenue-realized',
      label: 'Revenue Realized',
      value: '$48.9M',
      change: '+18.6%',
      direction: 'positive',
      description: 'Net ARR realized vs. plan with AI-assisted deal reviews.',
      sparkline: [24.5, 27.2, 30.4, 33.7, 37.9, 43.1, 48.9],
    },
    {
      id: 'onboarded',
      label: 'Accounts Activated',
      value: '482',
      change: '+64',
      direction: 'positive',
      description: 'Customers achieving first value within 30 days of go-live.',
      sparkline: [180, 221, 268, 321, 372, 427, 482],
    },
    {
      id: 'retention',
      label: 'Retention Health',
      value: '94.1%',
      change: '-1.1 pts',
      direction: 'negative',
      description: 'Churn pressure driven by macro-economic headwinds in APAC.',
      sparkline: [96, 95.6, 95.1, 94.8, 94.6, 94.4, 94.1],
    },
    {
      id: 'nps',
      label: 'Experience NPS',
      value: '64',
      change: '+2',
      direction: 'neutral',
      description: 'Executive alignment on high-touch journeys vs. Redwood peers.',
      sparkline: [57, 58, 59, 61, 62, 63, 64],
    },
  ],
};

const engagementViews = {
  nps: {
    title: 'Net Promoter Score',
    yLabel: 'NPS',
    series: [
      {
        label: 'Menmo Experience Cloud',
        color: '#2a5adf',
        data: [58, 59, 61, 64, 66, 70, 71],
      },
      {
        label: 'Redwood Benchmark',
        color: '#9ba3b5',
        data: [52, 53, 54, 55, 56, 57, 58],
      },
    ],
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
  },
  activation: {
    title: 'Activation Velocity',
    yLabel: 'Activation %',
    series: [
      {
        label: 'Concierge Orchestration',
        color: '#1ab97a',
        data: [42, 46, 51, 58, 63, 68, 72],
      },
      {
        label: 'Self-service Journeys',
        color: '#f06445',
        data: [22, 24, 28, 31, 36, 40, 44],
      },
    ],
    categories: ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4', 'Sprint 5', 'Sprint 6', 'Sprint 7'],
  },
};

const pipelineRecords = [
  {
    id: 'acme',
    name: 'ACME Robotics',
    segment: 'enterprise',
    owner: 'Priya Singh',
    stage: 'Orchestration',
    arr: 2400000,
    next: 'Joint exec review 08/19',
    health: 'good',
  },
  {
    id: 'northwind',
    name: 'Northwind Analytics',
    segment: 'growth',
    owner: 'Diego Martinez',
    stage: 'Design Sprint',
    arr: 780000,
    next: 'Finalize blueprint 08/14',
    health: 'watch',
  },
  {
    id: 'zenith',
    name: 'Zenith BioSystems',
    segment: 'enterprise',
    owner: 'Morgan Lee',
    stage: 'Value Assessment',
    arr: 3100000,
    next: 'Board alignment 08/25',
    health: 'good',
  },
  {
    id: 'stellar',
    name: 'Stellar Freight',
    segment: 'growth',
    owner: 'Kai Ito',
    stage: 'Negotiation',
    arr: 1150000,
    next: 'Pricing workshop 08/17',
    health: 'risk',
  },
  {
    id: 'lumen',
    name: 'Lumen Labs',
    segment: 'startup',
    owner: 'Olivia Chen',
    stage: 'Pilot',
    arr: 210000,
    next: 'Adoption review 08/20',
    health: 'watch',
  },
  {
    id: 'gravitate',
    name: 'Gravitate Media',
    segment: 'growth',
    owner: 'Remy Clarkson',
    stage: 'Commit',
    arr: 920000,
    next: 'MSA sign-off 08/11',
    health: 'good',
  },
];

const rhythmOfBusiness = [
  {
    id: 'ebc',
    title: 'Executive Business Review',
    date: 'Aug 12 • 10:00 PT',
    description: 'Align renewal runway and multi-solution expansion targets with ACME robotics.',
    owner: 'Priya Singh',
  },
  {
    id: 'launchpad',
    title: 'Launchpad Enablement',
    date: 'Aug 13 • 14:00 PT',
    description: 'Hand-off adoption playbooks and success plans for growth pod 3 accounts.',
    owner: 'Customer Experience Ops',
  },
  {
    id: 'ops-review',
    title: 'Weekly Ops Review',
    date: 'Aug 15 • 09:30 PT',
    description: 'Inspect active journey cadences, lead indicators, and backlog risk.',
    owner: 'Chief of Staff',
  },
  {
    id: 'service-huddle',
    title: 'Global Service Huddle',
    date: 'Aug 16 • 08:00 PT',
    description: 'Share AI-driven escalations and align coverage with regional leads.',
    owner: 'Service Excellence',
  },
];

const actionShortcuts = [
  {
    id: 'design-sprint',
    title: 'Assemble design sprint',
    details: 'Spin up cross-functional pod and assign discovery templates for Northwind.',
    due: 'Due today',
    impact: 'Growth • +$780k',
    cta: 'Launch sprint',
  },
  {
    id: 'recovery-plan',
    title: 'Activate recovery playbook',
    details: 'Enable executive sponsor outreach and curated enablement for Stellar Freight.',
    due: 'Due in 2 days',
    impact: 'Enterprise • Retain $1.1M',
    cta: 'Open playbook',
  },
  {
    id: 'nps-followup',
    title: 'Close the loop on NPS detractors',
    details: 'Summarized sentiment from July pulses with recommended outreach tasks.',
    due: 'Due this week',
    impact: 'Experience • +4 NPS',
    cta: 'Review insights',
  },
];

const aiHighlights = [
  {
    id: 'signal-expansion',
    tag: 'Expansion signal',
    summary:
      'Zenith BioSystems is exploring integrated analytics. Introduce advanced automation bundle in upcoming board review.',
  },
  {
    id: 'signal-risk',
    tag: 'Risk alert',
    summary:
      'Usage dip detected for Stellar Freight warehouse module. Recommend stand-up with solution architects within 48 hours.',
  },
  {
    id: 'signal-csat',
    tag: 'CSAT insight',
    summary:
      'Concierge onboarding cohort reporting 32% faster time-to-value than baseline; replicate for EMEA rollout.',
  },
];

function renderMetrics(range) {
  const container = document.getElementById('metricsGrid');
  container.innerHTML = '';
  const metrics = metricsByRange[range] ?? metricsByRange.week;

  metrics.forEach((metric) => {
    const card = document.createElement('article');
    card.className = `metric-card metric-card--${metric.direction}`;
    card.setAttribute('tabindex', '0');
    card.innerHTML = `
      <div class="metric-card__label">
        <span>${metric.label}</span>
      </div>
      <div class="metric-card__value">${metric.value}</div>
      <div class="metric-card__trend">${formatTrend(metric.change, metric.direction)}</div>
      <p class="metric-card__description">${metric.description}</p>
    `;

    const sparkline = createSparkline(metric.sparkline);
    card.appendChild(sparkline);
    container.appendChild(card);
  });
}

function formatTrend(change, direction) {
  const icons = {
    positive: '▲',
    negative: '▼',
    neutral: '◆',
  };
  return `${icons[direction] ?? ''} ${change}`;
}

function createSparkline(values) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 120 48');
  svg.setAttribute('aria-hidden', 'true');
  svg.classList.add('metric-card__sparkline');

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = 120 / (values.length - 1);

  const pathData = values
    .map((value, index) => {
      const x = step * index;
      const y = 48 - ((value - min) / range) * 46 - 1;
      return `${index === 0 ? 'M' : 'L'}${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(' ');

  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', pathData);
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke', 'var(--color-primary)');
  path.setAttribute('stroke-width', '2');
  path.setAttribute('stroke-linecap', 'round');
  svg.appendChild(path);

  const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
  const gradientId = `spark-${Math.random().toString(36).slice(2, 7)}`;
  gradient.setAttribute('id', gradientId);
  gradient.setAttribute('x1', '0');
  gradient.setAttribute('y1', '0');
  gradient.setAttribute('x2', '0');
  gradient.setAttribute('y2', '1');

  const stopTop = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
  stopTop.setAttribute('offset', '0%');
  stopTop.setAttribute('stop-color', 'var(--color-primary)');
  stopTop.setAttribute('stop-opacity', '0.35');

  const stopBottom = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
  stopBottom.setAttribute('offset', '100%');
  stopBottom.setAttribute('stop-color', 'var(--color-primary)');
  stopBottom.setAttribute('stop-opacity', '0');

  gradient.append(stopTop, stopBottom);

  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  defs.appendChild(gradient);
  svg.appendChild(defs);

  const areaPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  const areaData = `${pathData} L120 48 L0 48 Z`;
  areaPath.setAttribute('d', areaData);
  areaPath.setAttribute('fill', `url(#${gradientId})`);
  svg.insertBefore(areaPath, path);

  return svg;
}

function renderPipeline(segment) {
  const table = document.getElementById('pipelineTable');
  table.innerHTML = '';

  const header = document.createElement('div');
  header.className = 'table__header';
  header.innerHTML = `
    <div>Motion</div>
    <div>Owner</div>
    <div class="table__cell--hide-mobile">Stage</div>
    <div class="table__cell--hide-mobile">Next Milestone</div>
    <div>Health</div>
  `;
  table.appendChild(header);

  pipelineRecords
    .filter((record) => segment === 'all' || record.segment === segment)
    .forEach((record) => {
      const row = document.createElement('div');
      row.className = 'table__row';
      row.innerHTML = `
        <div>
          <div class="table__title">${record.name}</div>
          <div class="table__meta">${record.segment.toUpperCase()} • ${formatCurrency(
        record.arr
      )}</div>
        </div>
        <div>${record.owner}</div>
        <div class="table__cell--hide-mobile">${record.stage}</div>
        <div class="table__cell--hide-mobile">${record.next}</div>
        <div>${renderStatus(record.health)}</div>
      `;
      table.appendChild(row);
    });
}

function renderStatus(health) {
  const map = {
    good: { label: 'On track', className: 'status status--good', icon: '●' },
    watch: { label: 'Watch', className: 'status status--watch', icon: '●' },
    risk: { label: 'At risk', className: 'status status--risk', icon: '●' },
  };
  const status = map[health] ?? map.good;
  return `<span class="${status.className}"><span aria-hidden="true">${status.icon}</span>${status.label}</span>`;
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

function formatLegendValue(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return value ?? '';
  }
  if (value >= 1000) {
    return Math.round(value).toLocaleString('en-US');
  }
  if (Number.isInteger(value)) {
    return value.toString();
  }
  return value.toFixed(1);
}

function renderTimeline() {
  const container = document.getElementById('timeline');
  container.innerHTML = '';
  rhythmOfBusiness.forEach((event) => {
    const item = document.createElement('article');
    item.className = 'timeline__item';
    item.innerHTML = `
      <div class="timeline__title">${event.title}</div>
      <div class="timeline__meta">${event.date} • ${event.owner}</div>
      <p>${event.description}</p>
    `;
    container.appendChild(item);
  });
}

function renderActions() {
  const list = document.getElementById('actionList');
  list.innerHTML = '';
  actionShortcuts.forEach((action) => {
    const item = document.createElement('li');
    item.className = 'action-card';
    item.innerHTML = `
      <div class="action-card__title">${action.title}</div>
      <div class="action-card__body">${action.details}</div>
      <div class="action-card__meta">
        <span>${action.due}</span>
        <span>${action.impact}</span>
      </div>
      <button class="action-card__cta">${action.cta}</button>
    `;
    list.appendChild(item);
  });
}

function renderInsights() {
  const feed = document.getElementById('insightFeed');
  feed.innerHTML = '';
  aiHighlights.forEach((insight) => {
    const card = document.createElement('article');
    card.className = 'insight-card';
    card.innerHTML = `
      <span class="insight-card__tag">${insight.tag}</span>
      <p class="insight-card__body">${insight.summary}</p>
    `;
    feed.appendChild(card);
  });
}

function renderChart(viewKey) {
  const view = engagementViews[viewKey] ?? engagementViews.nps;
  const canvas = document.getElementById('pulseChart');
  drawLineChart(canvas, view);
  renderLegend(view);
}

function renderLegend(view) {
  const legend = document.getElementById('chartLegend');
  legend.innerHTML = '';
  const suffix = view.yLabel.includes('%') ? '%' : '';

  view.series.forEach((series) => {
    const item = document.createElement('div');
    item.className = 'chart-legend__item';
    const latest = series.data.at(-1);
    item.innerHTML = `
      <span class="chart-legend__swatch" style="background:${series.color}"></span>
      <div>
        <div>${series.label}</div>
        <div class="chart-legend__value">${formatLegendValue(latest)}${suffix}</div>
      </div>
    `;
    legend.appendChild(item);
  });
}

function drawLineChart(canvas, view) {
  const context = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const width = rect.width || canvas.clientWidth;
  const height = rect.height || canvas.clientHeight;
  if (!width || !height) {
    canvas.width = 0;
    canvas.height = 0;
    return;
  }
  const padding = { top: 20, right: 20, bottom: 36, left: 48 };

  canvas.width = width * dpr;
  canvas.height = height * dpr;
  context.setTransform(1, 0, 0, 1, 0, 0);
  context.scale(dpr, dpr);
  context.clearRect(0, 0, width, height);

  const styles = getComputedStyle(document.body);
  const allValues = view.series.flatMap((series) => series.data);
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const range = maxValue - minValue || 1;

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  context.strokeStyle = styles.getPropertyValue('--color-border');
  context.lineWidth = 1;
  context.beginPath();
  const steps = 4;
  for (let i = 0; i <= steps; i += 1) {
    const y = padding.top + (plotHeight / steps) * i;
    context.moveTo(padding.left, y);
    context.lineTo(width - padding.right, y);
  }
  context.stroke();

  context.fillStyle = styles.getPropertyValue('--color-text-muted');
  context.font = '12px Inter, system-ui';
  context.textAlign = 'right';
  context.textBaseline = 'middle';
  for (let i = 0; i <= steps; i += 1) {
    const value = maxValue - (range / steps) * i;
    const y = padding.top + (plotHeight / steps) * i;
    context.fillText(Math.round(value).toString(), padding.left - 10, y);
  }

  const divisor = Math.max(view.categories.length - 1, 1);
  const stepX = plotWidth / divisor;
  context.lineJoin = 'round';
  context.lineCap = 'round';

  view.series.forEach((series) => {
    context.beginPath();
    context.lineWidth = 2.5;
    context.strokeStyle = series.color;
    series.data.forEach((value, index) => {
      const x = padding.left + stepX * index;
      const y = padding.top + plotHeight - ((value - minValue) / range) * plotHeight;
      if (index === 0) {
        context.moveTo(x, y);
      } else {
        context.lineTo(x, y);
      }
    });
    context.stroke();

    series.data.forEach((value, index) => {
      const x = padding.left + stepX * index;
      const y = padding.top + plotHeight - ((value - minValue) / range) * plotHeight;
      context.beginPath();
      context.fillStyle = series.color;
      context.arc(x, y, 4, 0, Math.PI * 2);
      context.fill();
    });
  });

  context.fillStyle = styles.getPropertyValue('--color-text-muted');
  context.textAlign = 'center';
  context.textBaseline = 'top';
  view.categories.forEach((label, index) => {
    const x = padding.left + stepX * index;
    const y = height - padding.bottom + 12;
    context.fillText(label, x, y);
  });

  context.save();
  context.translate(16, height / 2);
  context.rotate((-90 * Math.PI) / 180);
  context.textAlign = 'center';
  context.fillText(view.yLabel, 0, 0);
  context.restore();
}

function setupMetricRange() {
  const select = document.getElementById('metricRange');
  select.addEventListener('change', () => {
    renderMetrics(select.value);
  });
}

function setupSegmentFilter() {
  const select = document.getElementById('segmentFilter');
  select.addEventListener('change', () => {
    renderPipeline(select.value);
  });
}

function setupEngagementToggle() {
  const buttons = document.querySelectorAll('.segmented-control__item');
  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      buttons.forEach((btn) => btn.setAttribute('aria-pressed', 'false'));
      button.setAttribute('aria-pressed', 'true');
      renderChart(button.dataset.view);
    });
  });
}

function setupThemeToggle() {
  const toggle = document.getElementById('toggleTheme');
  toggle.addEventListener('click', () => {
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
    toggle.setAttribute('aria-pressed', String(!isDark));
    renderChart(document.querySelector('.segmented-control__item[aria-pressed="true"]').dataset.view);
  });
}

function setupSidebarCollapse() {
  const collapse = document.getElementById('collapseSidebar');
  const sidebar = document.getElementById('sidebar');
  collapse.addEventListener('click', () => {
    const expanded = collapse.getAttribute('aria-expanded') === 'true';
    collapse.setAttribute('aria-expanded', String(!expanded));
    if (window.innerWidth < 720) {
      sidebar.dataset.open = expanded ? 'false' : 'true';
    } else {
      document.querySelector('.app-shell').style.gridTemplateColumns = expanded
        ? '88px 1fr'
        : 'var(--sidebar-width) 1fr';
      sidebar.classList.toggle('sidebar--collapsed', expanded);
    }
  });
}

function setupResponsiveSidebar() {
  const sidebar = document.getElementById('sidebar');
  const collapse = document.getElementById('collapseSidebar');
  const media = window.matchMedia('(max-width: 720px)');

  function handleChange(event) {
    const shell = document.querySelector('.app-shell');
    if (event.matches) {
      sidebar.dataset.open = 'false';
      shell.style.gridTemplateColumns = '1fr';
      collapse.setAttribute('aria-expanded', 'false');
      sidebar.classList.remove('sidebar--collapsed');
    } else {
      sidebar.dataset.open = '';
      shell.style.gridTemplateColumns = 'var(--sidebar-width) 1fr';
      collapse.setAttribute('aria-expanded', 'true');
      sidebar.classList.remove('sidebar--collapsed');
    }
  }

  media.addEventListener('change', handleChange);
  handleChange(media);
}

function setupNavInteractions() {
  const sidebar = document.getElementById('sidebar');
  const collapse = document.getElementById('collapseSidebar');
  document.querySelectorAll('.nav__item').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.nav__item').forEach((item) => item.classList.remove('nav__item--active'));
      button.classList.add('nav__item--active');
      if (window.innerWidth < 720 && sidebar) {
        sidebar.dataset.open = 'false';
        collapse?.setAttribute('aria-expanded', 'false');
      }
    });
  });
}

function setupResizeObserver() {
  if (typeof ResizeObserver === 'undefined') {
    return;
  }
  const canvas = document.getElementById('pulseChart');
  const observer = new ResizeObserver(() => {
    const activeView = document.querySelector('.segmented-control__item[aria-pressed="true"]').dataset.view;
    renderChart(activeView);
  });
  observer.observe(canvas);
}

function initialize() {
  document.body.setAttribute('data-theme', 'light');
  const themeToggle = document.getElementById('toggleTheme');
  if (themeToggle) {
    themeToggle.setAttribute('aria-pressed', 'false');
  }

  renderMetrics('week');
  renderPipeline('all');
  renderTimeline();
  renderActions();
  renderInsights();
  renderChart('nps');

  setupMetricRange();
  setupSegmentFilter();
  setupEngagementToggle();
  setupThemeToggle();
  setupSidebarCollapse();
  setupResponsiveSidebar();
  setupNavInteractions();
  setupResizeObserver();
}

window.addEventListener('DOMContentLoaded', initialize);
