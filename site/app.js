const { createApp, ref, computed, onMounted } = Vue;

const ORGS = ['IETF','APNIC','RIPE','ICANN','NANOG','MANRS'];

const App = {
  setup() {
    const locale = ref(localStorage.getItem('lang') || 'zh');
    const dict = ref({ zh:{}, en:{} });
    const meetings = ref([]);
    const meta = ref({ generated_at:'', count:0 });
    const activeOrg = ref('ALL');

    const t = k => dict.value[locale.value]?.[k] ?? k;
    const switchLang = () => {
      locale.value = locale.value==='zh' ? 'en' : 'zh';
      localStorage.setItem('lang', locale.value);
      document.documentElement.lang = locale.value;
    };
    const pick = o => { activeOrg.value = activeOrg.value===o ? 'ALL' : o; };

    const filtered = computed(() =>
      activeOrg.value==='ALL' ? meetings.value
                              : meetings.value.filter(m=>m.org===activeOrg.value)
    );
    const fmtDate = m => {
      const s=(m.start||'').slice(0,10), e=(m.end||'').slice(0,10);
      if(!s) return '';
      if(locale.value==='en'){
        const mo=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const d=x=>{const[y,mm,dd]=x.split('-');return `${mo[+mm-1]} ${+dd}, ${y}`};
        return s===e ? d(s) : `${d(s)} ~ ${d(e)}`;
      }
      return s===e ? s : `${s} ~ ${e}`;
    };

    onMounted(async () => {
      const [i18nRes,dataRes] = await Promise.all([
        fetch('./i18n.json?t='+Date.now()),
        fetch('./data.json?t='+Date.now())
      ]);
      dict.value = await i18nRes.json();
      const d = await dataRes.json();
      meetings.value = d.meetings || [];
      meta.value = { generated_at:d.generated_at, count:d.count ?? meetings.value.length };
      document.documentElement.lang = locale.value;
    });

    return { locale,t,switchLang,ORGS,activeOrg,pick,filtered,meta,fmtDate };
  },
  template: `
  <div class="head">
    <div>
      <h1>🗓️ {{ t('title') }}</h1>
      <div class="srcs" style="margin-top:8px">
        <a href="https://www.ietf.org/meeting/upcoming/" target="_blank">IETF</a>
        <a href="https://www.apnic.net/events/conferences/" target="_blank">APNIC</a>
        <a href="https://www.ripe.net/meetings/ripe-meetings/upcoming-ripe-meetings/" target="_blank">RIPE</a>
        <a href="https://meetings.icann.org/en/calendar" target="_blank">ICANN</a>
        <a href="https://nanog.org/events/future/?type=conference" target="_blank">NANOG</a>
        <a href="https://manrs.org/resources/events/" target="_blank">MANRS</a>
      </div>
    </div>
    <button class="langbtn" @click="switchLang">{{ t('switch') }}</button>
  </div>
  <div class="stat">
    {{ t('count_prefix') }} {{ meta.count }} {{ t('count_suffix') }} ·
    {{ t('gen_at') }}: {{ (meta.generated_at||'').replace('T',' ').slice(0,16) }} ·
    {{ t('window') }}
  </div>

  <div class="filters">
    <button :class="{on:activeOrg==='ALL'}" @click="activeOrg='ALL'">{{ t('all') }}</button>
    <button v-for="o in ORGS" :key="o" :class="{on:activeOrg===o}" @click="pick(o)">{{ o }}</button>
  </div>

  <div v-if="filtered.length">
    <article class="card" v-for="m in filtered" :key="m.id">
      <h3>
        <span class="pill" :class="'pill-'+m.org" @click="pick(m.org)">{{ m.org }}</span>
        <a :href="m.url" target="_blank" rel="noopener">{{ m.name }}</a>
      </h3>
      <div class="meta">📅 {{ fmtDate(m) }}</div>
      <div class="meta">
        📍 <span :class="{loc:true, tbd:!m.location || m.location==='TBD'}">
          {{ m.location && m.location!=='TBD' ? m.location : 'TBD' }}
        </span>
      </div>
    </article>
  </div>
  <div v-else class="empty">{{ t('empty') }}</div>

  <section class="about">
    <b>ℹ️ {{ t('about_title') }}</b>
    <div>{{ t('about_body') }}</div>
  </section>
  `
};

createApp(App).mount('#app');
