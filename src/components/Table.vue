<script>
export default {
  name: 'ProductTable',
  props: {
    // Endpoint that returns an array of products as JSON.
    // Expected shape (fields can be remapped below): 
    // [{ title, price, image, website, link }, ...]
    apiUrl: {
      type: String,
      default: 'http://localhost:5000/search'
    },
    // The product/item to search for, e.g. "Shocq Triumph Recurve Limbs".
    // Sent to the API as ?item=...
    searchItem: {
      type: String,
      default: ''
    },
    // Which wordlist/site category to search, e.g. "recurve_limbs".
    // Sent to the API as ?category=... Acts as the initial value for the
    // category dropdown; use v-model:category on the parent if you want
    // to control it there instead.
    category: {
      type: String,
      default: 'recurve_limbs'
    },
    // Options shown in the category dropdown. Each 'value' should match
    // a wordlist category your backend's find_wordlist() understands.
    categories: {
      type: Array,
      default: () => ([
        { value: 'recurve_limbs', label: 'Recurve Limbs' },
        { value: 'recurve_risers', label: 'Recurve Risers' },
        { value: 'compound_bows', label: 'Compound Bows' },
        { value: 'arrows', label: 'Arrows' },
        { value: 'bow_strings', label: 'Bow Strings' },
        { value: 'recurve_sights', label: 'Recurve Sights' },
        { value: 'compound_sights', label: 'Compound Sights' },
        { value: 'stabilizers', label: 'Stabilizers' },
        { value: 'quivers', label: 'Quivers' },
        { value: 'arrow_rests', label: 'Arrow Rests' },
        { value: 'tabs_gloves', label: 'Tabs & Gloves' },
        { value: 'armguards', label: 'Armguards' },
      ])
    },
    // Optional: pass products directly instead of (or in addition to) fetching.
    // Useful for SSR, tests, or when the parent already has the data.
    products: {
      type: Array,
      default: null
    },
    // Optional fetch options (headers, auth, etc.)
    fetchOptions: {
      type: Object,
      default: () => ({})
    },
    // Auto-fetch on mount if apiUrl is provided
    autoFetch: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:category'],
  data() {
    return {
      items: [],
      loading: false,
      error: null,
      query: '',
      debounceTimer: null,
      selectedCategory: this.category,
      sortKey: 'title',
      sortDir: 'asc',
      columns: [
        { key: 'image', label: 'Image', sortable: false },
        { key: 'title', label: 'Title', sortable: true },
        { key: 'price', label: 'Price', sortable: true },
        { key: 'website', label: 'Website', sortable: true },
        { key: 'link', label: 'Link', sortable: false },
      ],
    };
  },
  computed: {
    filtered() {
      let result = this.items;

      if (this.sortKey) {
        result = [...result].sort((a, b) => {
          let va = a[this.sortKey];
          let vb = b[this.sortKey];

          if (this.sortKey === 'price') {
            va = Number(va) || 0;
            vb = Number(vb) || 0;
            return this.sortDir === 'asc' ? va - vb : vb - va;
          }

          const cmp = String(va ?? '').localeCompare(String(vb ?? ''));
          return this.sortDir === 'asc' ? cmp : -cmp;
        });
      }

      return result;
    }
  },
  created() {
    if (this.apiUrl && this.autoFetch && !this.products) {
      this.fetchProducts();
    }
  },
  watch: {
    // Allow parent-provided products to update the table reactively
    products: {
      immediate: true,
      handler(newVal) {
        if (Array.isArray(newVal)) {
          this.items = this.normalize(newVal);
        }
      }
    },
    searchItem() {
      if (this.apiUrl && this.autoFetch && !this.products) {
        this.fetchProducts();
      }
    },
    category(newVal) {
      // Parent changed the prop (e.g. via v-model:category) — keep the
      // dropdown in sync without re-triggering itself in a loop.
      if (newVal !== this.selectedCategory) {
        this.selectedCategory = newVal;
      }
    },
    selectedCategory(newVal) {
      this.$emit('update:category', newVal);
      if (this.apiUrl && this.autoFetch && !this.products) {
        this.fetchProducts();
      }
    },
    query() {
      if (!this.apiUrl || this.products) return;
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        this.fetchProducts();
      }, 1000);
    }
  },
  beforeUnmount() {
    clearTimeout(this.debounceTimer);
  },
  methods: {
    normalize(rawList) {
      // Adjust these mappings if your API uses different field names,
      // e.g. p.name instead of p.title, or p.url instead of p.link.
      return rawList.map((p, i) => ({
        id: p.id ?? i,
        title: p.title ?? p.name ?? 'Untitled',
        price: p.price ?? p.cost ?? 0,
        image: p.image ?? p.imageUrl ?? p.thumbnail ?? '',
        website: p.website ?? this.hostFromUrl(p.link ?? p.url) ?? '',
        link: p.link ?? p.url ?? '#',
      }));
    },
    hostFromUrl(url) {
      if (!url) return '';
      try {
        return new URL(url).hostname.replace(/^www\./, '');
      } catch {
        return '';
      }
    },
    formatPrice(price) {
      const num = Number(price);
      if (Number.isNaN(num)) return price;
      return num.toLocaleString(undefined, { style: 'currency', currency: 'GBP' });
    },
    async fetchProducts() {
      if (!this.apiUrl) return;
      const term = this.query.trim() || this.searchItem;
      if (!term) {
        this.items = [];
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        const url = new URL(this.apiUrl, window.location.origin);
        url.searchParams.set('item', term);
        if (this.selectedCategory) url.searchParams.set('category', this.selectedCategory);

        const res = await fetch(url.toString(), this.fetchOptions);
        if (!res.ok) {
          const body = await res.json().catch(() => null);
          throw new Error((body && body.error) || `Request failed with status ${res.status}`);
        }
        const data = await res.json();
        const list = Array.isArray(data) ? data : (data.products || data.items || data.results || []);
        this.items = this.normalize(list);
      } catch (err) {
        this.error = err.message || 'Failed to load products.';
      } finally {
        this.loading = false;
      }
    },
    sortBy(col) {
      if (!col.sortable) return;
      if (this.sortKey === col.key) {
        this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = col.key;
        this.sortDir = 'asc';
      }
    }
  }
};
</script>

<template>
  <div class="product-table">
    <div class="table-head">
      <div>
        <h1>Product catalog</h1>
        <p v-if="!loading && !error">{{ items.length }} products found</p>
      </div>
      <div class="head-actions">
        <select v-model="selectedCategory" class="category-select" aria-label="Product category">
          <option v-for="opt in categories" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        <div class="search-box">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="7" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input v-model="query" type="text" placeholder="Search for a product…" />
          <span v-if="loading" class="search-spinner">Searching…</span>
        </div>
        <button v-if="apiUrl" class="refresh-btn" @click="fetchProducts" :disabled="loading">
          {{ loading ? 'Loading…' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div class="table-wrap">
      <div v-if="loading && items.length === 0" class="state-message">Loading products…</div>
      <div v-else-if="error" class="state-message error">
        {{ error }}
        <button class="retry-btn" @click="fetchProducts">Retry</button>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :class="{ active: sortKey === col.key, sortable: col.sortable }"
              @click="sortBy(col)"
            >
              {{ col.label }}
              <span class="arrow" v-if="col.sortable && sortKey === col.key">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in filtered" :key="product.id">
            <td class="image-cell">
              <img v-if="product.image" :src="product.image" :alt="product.title" />
              <div v-else class="image-placeholder">No image</div>
            </td>
            <td class="title-cell">{{ product.title }}</td>
            <td class="price-cell">{{ formatPrice(product.price) }}</td>
            <td class="website-cell">{{ product.website }}</td>
            <td class="link-cell">
              <a :href="product.link" target="_blank" rel="noopener noreferrer">View →</a>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="5" class="empty">
              {{ query.trim() ? `No products match "${query}".` : 'Type in the search box to find a product.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.product-table {
  --ink: #1c2321;
  --ink-soft: #57625e;
  --paper: #f6f5f1;
  --line: #d8d4c8;
  --accent: #2f5d50;
  --accent-soft: #e4ede9;
  --danger: #a13f3f;
  --font-display: 'Iowan Old Style', 'Georgia', serif;
  --font-body: 'Charter', 'Georgia', serif;
  --font-mono: ui-monospace, 'SF Mono', Menlo, monospace;

  max-width: 960px;
  margin: 0 auto;
  color: var(--ink);
  font-family: var(--font-body);
}

.table-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.table-head h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 28px;
  margin: 0 0 4px;
  letter-spacing: 0.2px;
}

.table-head p {
  margin: 0;
  color: var(--ink-soft);
  font-size: 14px;
}

.head-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.category-select {
  font-family: var(--font-body);
  font-size: 14px;
  padding: 9px 12px;
  border: 1px solid var(--line);
  border-radius: 3px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
}

.category-select:focus {
  outline: none;
  border-color: var(--accent);
}

.search-box {
  position: relative;
}

.search-box input {
  font-family: var(--font-body);
  font-size: 14px;
  padding: 9px 12px 9px 32px;
  border: 1px solid var(--line);
  border-radius: 3px;
  background: #fff;
  width: 200px;
  color: var(--ink);
}

.search-box input:focus {
  outline: none;
  border-color: var(--accent);
}

.search-box svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.search-spinner {
  position: absolute;
  right: -78px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: var(--ink-soft);
  white-space: nowrap;
}

.refresh-btn {
  font-family: var(--font-body);
  font-size: 13px;
  padding: 9px 14px;
  border: 1px solid var(--accent);
  color: var(--accent);
  background: #fff;
  border-radius: 3px;
  cursor: pointer;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--accent-soft);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.table-wrap {
  border: 1px solid var(--line);
  border-radius: 4px;
  overflow: hidden;
  background: #fff;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14.5px;
}

thead th {
  text-align: left;
  padding: 12px 16px;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 13px;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--line);
  background: #efece3;
  user-select: none;
  white-space: nowrap;
}

thead th.sortable {
  cursor: pointer;
}

thead th.sortable:hover {
  color: var(--ink);
}

thead th .arrow {
  display: inline-block;
  margin-left: 4px;
  font-size: 11px;
  opacity: 0.5;
}

thead th.active .arrow {
  opacity: 1;
  color: var(--accent);
}

tbody td {
  padding: 10px 16px;
  border-bottom: 1px solid #ece9df;
  vertical-align: middle;
}

tbody tr:last-child td {
  border-bottom: none;
}

tbody tr:hover {
  background: #faf9f5;
}

.image-cell img {
  width: 44px;
  height: 44px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--line);
  display: block;
}

.image-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 4px;
  border: 1px dashed var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: var(--ink-soft);
  text-align: center;
}

.title-cell {
  font-weight: 600;
}

.price-cell {
  font-family: var(--font-mono);
  font-size: 13.5px;
  color: var(--ink);
}

.website-cell {
  color: var(--ink-soft);
  font-size: 13.5px;
}

.link-cell a {
  color: var(--accent);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 600;
}

.link-cell a:hover {
  text-decoration: underline;
}

.state-message {
  padding: 40px 16px;
  text-align: center;
  color: var(--ink-soft);
  font-size: 14px;
}

.state-message.error {
  color: var(--danger);
}

.retry-btn {
  display: block;
  margin: 12px auto 0;
  font-family: var(--font-body);
  font-size: 13px;
  padding: 7px 14px;
  border: 1px solid var(--danger);
  color: var(--danger);
  background: #fff;
  border-radius: 3px;
  cursor: pointer;
}

.empty {
  padding: 40px 16px;
  text-align: center;
  color: var(--ink-soft);
  font-size: 14px;
}
</style>