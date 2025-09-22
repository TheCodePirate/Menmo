const appShell = document.querySelector('.app-shell');
const sidebar = document.querySelector('.shell__sidebar');
const themeToggle = document.getElementById('themeToggle');
const mobileMenu = document.getElementById('mobileMenu');
const healthFilter = document.getElementById('healthFilter');
const performancePeriod = document.getElementById('performancePeriod');
const programmeTableBody = document.getElementById('programmeTableBody');
const workflowList = document.getElementById('workflowList');
const insightsGrid = document.getElementById('insightsGrid');
const activityTimeline = document.getElementById('activityTimeline');
const portfolioGrid = document.getElementById('portfolioGrid');
const footerYear = document.getElementById('footerYear');
const commandPalette = document.getElementById('commandPalette');
const commandPaletteButton = document.getElementById('commandPaletteButton');
const commandPaletteSearch = document.getElementById('commandPaletteSearch');
const commandPaletteList = document.getElementById('commandPaletteList');
const commandTemplate = document.getElementById('commandTemplate');
const globalSearch = document.getElementById('globalSearch');
const quickAction = document.getElementById('quickAction');
const openCreateModal = document.getElementById('openCreateModal');
const createModal = document.getElementById('createModal');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');
const refreshActivity = document.getElementById('refreshActivity');
const pulseToggle = document.getElementById('pulseToggle');

footerYear.textContent = new Date().getFullYear();

const state = {
  programmes: [
    {
      name: 'Global Commerce Re-platform',
      owner: 'Luna Larson',
      status: 'on-track',
      automation: 0.68,
      budget: '$2.6M',
      forecast: '-4.8% under',
    },
    {
      name: 'Predictive Inventory Network',
      owner: 'Zayn Ellison',
      status: 'at-risk',
      automation: 0.42,
      budget: '$1.9M',
      forecast: '+3.2% over',
    },
    {
      name: 'Finance Intelligence Fabric',
      owner: 'Ivy Chen',
      status: 'on-track',
      automation: 0.74,
      budget: '$2.1M',
      forecast: '-7.4% under',
    },
    {
      name: 'Automated Supplier Exchange',
      owner: 'Diego Alvarez',
      status: 'blocked',
      automation: 0.33,
      budget: '$1.2M',
      forecast: '+9.0% over',
    },
    {
      name: 'Customer Journey Orchestration',
      owner: 'Priya Desai',
      status: 'on-track',
      automation: 0.58,
      budget: '$980K',
      forecast: '-1.6% under',
    },
  ],
  workflows: [
    {
      title: 'Invoice validation copilot',
      detail: 'Uses document AI to reconcile invoices to purchase orders in real time.',
      meta: ['Finance', 'Saved 420 hours', '99.2% accuracy'],
    },
    {
      title: 'Predictive talent mobility',
      detail: 'Aggregates performance data to surface succession candidates automatically.',
      meta: ['People', '+18% internal mobility', 'Live in 6 regions'],
    },
    {
      title: 'Logistics exception routing',
      detail: 'Proactively reroutes shipments when fulfilment SLAs fall below thresholds.',
      meta: ['Operations', '-12% delays', 'AI-driven'],
    },
  ],
  insights: [
    {
      label: 'Engagement driver',
      value: 'Growth conversations every 45 days correlate to +11% retention.',
    },
    {
      label: 'Automation opportunity',
      value: 'Manual approvals in Finance Ops consume 290 hours per month.',
    },
    {
      label: 'Talent risk',
      value: 'Two critical squads exceed 35% attrition risk; succession ready in 60 days.',
    },
    {
      label: 'Experience pulse',
      value: 'Service NPS +9 vs industry benchmark over the last quarter.',
    },
  ],
  activities: [
    {
      title: 'Operations automation pushed',
      detail: 'New SLA guardrails deployed across fulfilment centres.',
      timestamp: '2h ago • Automation',
    },
    {
      title: 'Budget revision approved',
      detail: 'Finance authorised a 6% increase to meet accelerated go-live.',
      timestamp: '6h ago • Finance',
    },
    {
      title: 'Talent heatmap refreshed',
      detail: 'Live data sync complete for EMEA and APAC squads.',
      timestamp: '12h ago • People',
    },
    {
      title: 'Executive sync recorded',
      detail: 'Highlights alignment improvements and next quarter bets.',
      timestamp: '1d ago • Leadership',
    },
  ],
  portfolios: [
    {
      name: 'Connected Commerce',
      health: 'Stable',
      trend: '+6.4% velocity',
      summary: 'Marketplace, storefront and loyalty roadmaps shipped on schedule.',
    },
    {
      name: 'Intelligent Operations',
      health: 'Accelerating',
      trend: '+11% automation coverage',
      summary: 'Network digitisation unlocking faster fulfilment and fewer escalations.',
    },
    {
      name: 'Finance Transformation',
      health: 'Watchlist',
      trend: '-2.1% forecast',
      summary: 'Need to stabilise supplier integration before scaling next phase.',
    },
  ],
  commands: [
    { label: 'Create initiative', description: 'Launch the initiative wizard', action: () => openModal() },
    {
      label: 'Open automations',
      description: 'Jump to automation workflows',
      action: () => scrollToSection('#workflows'),
    },
    {
      label: 'View portfolio health',
      description: 'Focus the portfolio section',
      action: () => scrollToSection('#portfolioHealth'),
    },
    { label: 'Toggle theme', description: 'Switch between light and dark mode', action: () => toggleTheme() },
  ],
  sort: {
    key: null,
    direction: 'asc',
  },
};

const formatStatus = (status) => {
  const map = {
    'on-track': 'status status--on-track',
    'at-risk': 'status status--at-risk',
    blocked: 'status status--blocked',
  };
  const label = {
    'on-track': 'On track',
    'at-risk': 'At risk',
    blocked: 'Blocked',
  };
  return `<span class="${map[status]}">${label[status]}</span>`;
};

const formatAutomation = (value) => `${Math.round(value * 100)}%`;

const renderProgrammeTable = () => {
  const query = globalSearch.value.trim().toLowerCase();
  const filter = healthFilter.value;
  const programmes = state.programmes
    .filter((programme) =>
      query
        ? programme.name.toLowerCase().includes(query) ||
          programme.owner.toLowerCase().includes(query)
        : true,
    )
    .filter((programme) => (filter === 'all' ? true : programme.status === filter));

  const sorted = [...programmes];
  if (state.sort.key) {
    sorted.sort((a, b) => {
      const { key, direction } = state.sort;
      const order = direction === 'asc' ? 1 : -1;

      if (key === 'automation') {
        return (a[key] - b[key]) * order;
      }

      const valueA = a[key].toString().toLowerCase();
      const valueB = b[key].toString().toLowerCase();

      if (valueA < valueB) return -1 * order;
      if (valueA > valueB) return 1 * order;
      return 0;
    });
  }

  programmeTableBody.innerHTML = sorted
    .map(
      (programme) => `
        <tr>
          <th scope="row">${programme.name}</th>
          <td>${programme.owner}</td>
          <td>${formatStatus(programme.status)}</td>
          <td>${formatAutomation(programme.automation)}</td>
          <td>${programme.budget}</td>
          <td>${programme.forecast}</td>
        </tr>
      `,
    )
    .join('');
};

const renderWorkflows = () => {
  workflowList.innerHTML = state.workflows
    .map(
      (workflow) => `
        <li>
          <strong>${workflow.title}</strong>
          <p>${workflow.detail}</p>
          <div class="workflow__meta">
            ${workflow.meta.map((item) => `<span>${item}</span>`).join('')}
          </div>
        </li>
      `,
    )
    .join('');
};

const renderInsights = () => {
  insightsGrid.innerHTML = state.insights
    .map(
      (insight) => `
        <article class="insight">
          <span class="tag">${insight.label}</span>
          <strong>${insight.value}</strong>
        </article>
      `,
    )
    .join('');
};

const renderActivities = () => {
  activityTimeline.innerHTML = state.activities
    .map(
      (activity) => `
        <li>
          <strong>${activity.title}</strong>
          <p>${activity.detail}</p>
          <span class="timeline__meta">${activity.timestamp}</span>
        </li>
      `,
    )
    .join('');
};

const renderPortfolio = () => {
  portfolioGrid.innerHTML = state.portfolios
    .map(
      (portfolio) => `
        <article class="portfolio-card">
          <div class="portfolio-card__header">
            <strong>${portfolio.name}</strong>
            <span class="portfolio-card__badge">${portfolio.health}</span>
          </div>
          <p class="portfolio-card__trend">${portfolio.trend}</p>
          <p>${portfolio.summary}</p>
        </article>
      `,
    )
    .join('');
};

const renderCommands = (commands = state.commands) => {
  commandPaletteList.innerHTML = '';
  commands.forEach((command) => {
    const commandNode = commandTemplate.content.cloneNode(true);
    const button = commandNode.querySelector('button');
    button.innerHTML = `
      <span>${command.label}</span>
      <small>${command.description}</small>
    `;
    button.addEventListener('click', () => {
      command.action?.();
      hideCommandPalette();
    });
    commandPaletteList.appendChild(commandNode);
  });
};

const filterCommands = () => {
  const query = commandPaletteSearch.value.trim().toLowerCase();
  if (!query) {
    renderCommands();
    return;
  }
  const filtered = state.commands.filter((command) =>
    command.label.toLowerCase().includes(query) ||
    command.description.toLowerCase().includes(query),
  );
  renderCommands(filtered);
};

const showCommandPalette = () => {
  commandPalette.hidden = false;
  commandPaletteSearch.value = '';
  renderCommands();
  requestAnimationFrame(() => commandPaletteSearch.focus());
  document.addEventListener('keydown', handleCommandEscape);
};

const hideCommandPalette = () => {
  commandPalette.hidden = true;
  document.removeEventListener('keydown', handleCommandEscape);
};

const handleCommandEscape = (event) => {
  if (event.key === 'Escape') {
    hideCommandPalette();
  }
};

commandPalette.addEventListener('click', (event) => {
  if (event.target === commandPalette) {
    hideCommandPalette();
  }
});

commandPaletteSearch.addEventListener('input', filterCommands);
commandPaletteButton.addEventListener('click', showCommandPalette);
quickAction.addEventListener('click', showCommandPalette);

document.addEventListener('keydown', (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    if (commandPalette.hidden) {
      showCommandPalette();
    } else {
      hideCommandPalette();
    }
  }
});

const showToast = (message) => {
  toastMessage.textContent = message;
  toast.hidden = false;
  setTimeout(() => {
    toast.hidden = true;
  }, 2800);
};

const openModal = () => {
  if (typeof createModal.showModal === 'function') {
    createModal.showModal();
  } else {
    showToast('Modal is not supported in this browser.');
  }
};

const closeModal = () => createModal.close();

createModal.addEventListener('close', () => {
  if (createModal.returnValue === 'cancel') return;
  showToast('Initiative created successfully.');
});

createModal.addEventListener('submit', (event) => {
  event.preventDefault();
  closeModal();
});

openCreateModal.addEventListener('click', openModal);

const applyTheme = (theme) => {
  appShell.dataset.theme = theme;
  localStorage.setItem('menmo-theme', theme);
  themeToggle.setAttribute('aria-pressed', theme === 'dark');
  themeToggle.querySelector('.theme-toggle__icon').textContent =
    theme === 'dark' ? '🌙' : '🌞';
};

const toggleTheme = () => {
  const theme = appShell.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(theme);
};

themeToggle.addEventListener('click', toggleTheme);

const savedTheme = localStorage.getItem('menmo-theme');
if (savedTheme === 'dark') {
  applyTheme('dark');
}

mobileMenu.addEventListener('click', () => {
  sidebar.classList.toggle('is-open');
});

const closeSidebarOnOutsideClick = (event) => {
  if (!sidebar.contains(event.target) && !mobileMenu.contains(event.target)) {
    sidebar.classList.remove('is-open');
  }
};

document.addEventListener('click', (event) => {
  if (window.innerWidth <= 1200) {
    closeSidebarOnOutsideClick(event);
  }
});

const sortBy = (key) => {
  if (state.sort.key === key) {
    state.sort.direction = state.sort.direction === 'asc' ? 'desc' : 'asc';
  } else {
    state.sort.key = key;
    state.sort.direction = 'asc';
  }
  renderProgrammeTable();
};

Array.from(document.querySelectorAll('.table th[data-sort]')).forEach((header) => {
  header.addEventListener('click', () => sortBy(header.dataset.sort));
});

healthFilter.addEventListener('change', renderProgrammeTable);
globalSearch.addEventListener('input', renderProgrammeTable);

const performanceConfig = {
  month: {
    labels: ['Squad Atlas', 'Squad Nova', 'Squad Pulse', 'Squad Flux'],
    datasets: [
      {
        label: 'Velocity',
        data: [82, 76, 88, 71],
        backgroundColor: 'rgba(59, 130, 246, 0.65)',
      },
      {
        label: 'Quality',
        data: [93, 89, 97, 90],
        backgroundColor: 'rgba(16, 185, 129, 0.65)',
      },
      {
        label: 'Capacity',
        data: [78, 82, 75, 80],
        backgroundColor: 'rgba(251, 191, 36, 0.75)',
      },
    ],
  },
  quarter: {
    labels: ['Squad Atlas', 'Squad Nova', 'Squad Pulse', 'Squad Flux'],
    datasets: [
      {
        label: 'Velocity',
        data: [79, 74, 85, 70],
        backgroundColor: 'rgba(59, 130, 246, 0.65)',
      },
      {
        label: 'Quality',
        data: [91, 88, 95, 89],
        backgroundColor: 'rgba(16, 185, 129, 0.65)',
      },
      {
        label: 'Capacity',
        data: [75, 80, 74, 79],
        backgroundColor: 'rgba(251, 191, 36, 0.75)',
      },
    ],
  },
  year: {
    labels: ['Squad Atlas', 'Squad Nova', 'Squad Pulse', 'Squad Flux'],
    datasets: [
      {
        label: 'Velocity',
        data: [74, 72, 81, 68],
        backgroundColor: 'rgba(59, 130, 246, 0.65)',
      },
      {
        label: 'Quality',
        data: [88, 85, 92, 86],
        backgroundColor: 'rgba(16, 185, 129, 0.65)',
      },
      {
        label: 'Capacity',
        data: [72, 76, 70, 74],
        backgroundColor: 'rgba(251, 191, 36, 0.75)',
      },
    ],
  },
};

let performanceChartInstance;

const renderPerformanceChart = (period = 'month') => {
  const ctx = document.getElementById('performanceChart');
  const config = performanceConfig[period];

  if (!performanceChartInstance) {
    performanceChartInstance = new Chart(ctx, {
      type: 'radar',
      data: config,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            angleLines: { color: 'rgba(148, 163, 184, 0.16)' },
            grid: { color: 'rgba(148, 163, 184, 0.16)' },
            suggestedMax: 100,
            ticks: {
              backdropColor: 'transparent',
              color: 'var(--color-text-subtle)',
            },
            pointLabels: {
              color: 'var(--color-text-subtle)',
              font: { size: 12 },
            },
          },
        },
        plugins: {
          legend: { display: false },
        },
      },
    });
  } else {
    performanceChartInstance.data = config;
    performanceChartInstance.update();
  }

  renderLegend(config.datasets);
};

const renderLegend = (datasets) => {
  const legend = document.getElementById('performanceLegend');
  legend.innerHTML = datasets
    .map(
      (dataset) => `
        <li>
          <span class="legend__dot" style="background:${dataset.backgroundColor}"></span>
          <span>${dataset.label}</span>
        </li>
      `,
    )
    .join('');
};

performancePeriod.addEventListener('change', (event) => {
  renderPerformanceChart(event.target.value);
});

refreshActivity.addEventListener('click', () => {
  state.activities.unshift({
    title: 'AI guardrails tuned',
    detail: 'Automation policies updated to reflect new compliance thresholds.',
    timestamp: 'Just now • Automation',
  });
  if (state.activities.length > 6) {
    state.activities.pop();
  }
  renderActivities();
  showToast('Activity stream refreshed.');
});

pulseToggle.addEventListener('change', (event) => {
  if (event.target.checked) {
    showToast('Live pulse streaming enabled.');
  } else {
    showToast('Live pulse streaming paused.');
  }
});

const scrollToSection = (selector) => {
  const element = document.querySelector(selector);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

renderProgrammeTable();
renderWorkflows();
renderInsights();
renderActivities();
renderPortfolio();
renderPerformanceChart();
renderCommands();

if (!('showModal' in HTMLDialogElement.prototype)) {
  createModal.setAttribute('open', '');
  createModal.querySelector('.modal__footer').hidden = true;
  createModal.querySelector('form').setAttribute('aria-live', 'polite');
}
