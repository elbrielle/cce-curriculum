const searchToggle = document.querySelector('[data-search-toggle]');
const searchPanel = document.querySelector('[data-search-panel]');
const searchInput = document.querySelector('[data-search-input]');
const searchResults = document.querySelector('[data-search-results]');
const menuToggle = document.querySelector('[data-menu-toggle]');
const siteNav = document.querySelector('[data-site-nav]');

if (menuToggle && siteNav) {
  menuToggle.addEventListener('click', () => {
    const open = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-expanded', String(!open));
    siteNav.toggleAttribute('data-open', !open);
  });
}

if (searchToggle && searchPanel) {
  searchToggle.addEventListener('click', () => {
    const open = !searchPanel.hidden;
    searchPanel.hidden = open;
    searchToggle.setAttribute('aria-expanded', String(!open));
    if (!open) searchInput?.focus();
  });
}

let searchIndex = [];
async function ensureSearchIndex() {
  if (searchIndex.length) return searchIndex;
  const indexUrl = document.documentElement.dataset.searchIndex;
  if (!indexUrl) return [];
  const response = await fetch(indexUrl);
  searchIndex = await response.json();
  return searchIndex;
}

function renderSearchResults(items, query) {
  if (!searchResults) return;
  if (!query) {
    searchResults.innerHTML = '<p class="search-hint">Search by career, skill, week, TEKS, or lesson title.</p>';
    return;
  }
  if (!items.length) {
    searchResults.innerHTML = '<p class="search-hint">No matching curriculum pages.</p>';
    return;
  }
  searchResults.innerHTML = items.slice(0, 10).map((item) => `
    <a class="search-result" href="${item.url}">
      <span>${item.eyebrow}</span>
      <strong>${item.title}</strong>
      <small>${item.summary}</small>
    </a>`).join('');
}

searchInput?.addEventListener('input', async (event) => {
  const query = event.target.value.trim().toLowerCase();
  const index = await ensureSearchIndex();
  const terms = query.split(/\s+/).filter(Boolean);
  const matches = index.filter((item) => terms.every((term) => item.search.includes(term)));
  renderSearchResults(matches, query);
});

document.querySelectorAll('[data-curriculum-filter]').forEach((input) => {
  input.addEventListener('input', (event) => {
    const query = event.target.value.trim().toLowerCase();
    document.querySelectorAll('[data-week-row]').forEach((row) => {
      row.hidden = Boolean(query) && !row.dataset.search.includes(query);
    });
    document.querySelectorAll('[data-six-weeks-section]').forEach((section) => {
      const visible = [...section.querySelectorAll('[data-week-row]')].some((row) => !row.hidden);
      section.hidden = !visible;
    });
  });
});

const currentPage = window.location.pathname.replace(/index\.html$/, '');
document.querySelectorAll('[data-site-nav] a').forEach((link) => {
  const target = new URL(link.href).pathname.replace(/index\.html$/, '');
  if (target === currentPage) link.setAttribute('aria-current', 'page');
});
