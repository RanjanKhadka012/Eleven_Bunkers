import nuclearRaw from '../scenarios/narratives/Nuclear_Fallout.txt?raw'
import pandemicRaw from '../scenarios/narratives/Worldwide_Pandemic.txt?raw'
import aiRaw from '../scenarios/narratives/AI_Takeover.txt?raw'
import zombieRaw from '../scenarios/narratives/Zombie_Outbreak.txt?raw'
import alienRaw from '../scenarios/narratives/Alien_Invasion.txt?raw'
import resourceRaw from '../scenarios/narratives/Resource_War.txt?raw'
import climateRaw from '../scenarios/narratives/Climate_Collapse.txt?raw'

function parseNarrative(raw) {
  const sections = { opening: '', explanation: '', endingWin: '', endingLoss: '' }
  let current = null

  raw.split(/\r?\n/).forEach((line) => {
    const trimmed = line.trim()

    if (/^opening:/i.test(trimmed)) {
      current = 'opening'
      return
    }
    if (/^scenario explanation:/i.test(trimmed)) {
      current = 'explanation'
      return
    }
    if (/^ending - win:/i.test(trimmed)) {
      current = 'endingWin'
      return
    }
    if (/^ending - loss:/i.test(trimmed)) {
      current = 'endingLoss'
      return
    }

    if (!current || !trimmed) {
      return
    }

    sections[current] = sections[current] ? `${sections[current]} ${trimmed}` : trimmed
  })

  return sections
}

const SCENARIO_SOURCES = [
  {
    slug: 'nuclear_fallout',
    label: 'Ashes of Silence',
    matches: ['nuclear war', 'nuclear'],
    raw: nuclearRaw,
  },
  {
    slug: 'worldwide_pandemic',
    label: 'The Last Breath Protocol',
    matches: ['global pandemic', 'pandemic', 'virus'],
    raw: pandemicRaw,
  },
  {
    slug: 'ai_takeover',
    label: 'Protocol: Extinction',
    matches: ['ai takeover', 'ai'],
    raw: aiRaw,
  },
  {
    slug: 'zombie_outbreak',
    label: 'Evolved Hunger',
    matches: ['zombie apocalypse', 'zombie'],
    raw: zombieRaw,
  },
  {
    slug: 'alien_invasion',
    label: 'Harvest Cycle',
    matches: ['alien invasion', 'alien'],
    raw: alienRaw,
  },
  {
    slug: 'resource_war',
    label: 'Dust Dominion',
    matches: ['resource war', 'mad max', 'war'],
    raw: resourceRaw,
  },
  {
    slug: 'climate_collapse',
    label: 'The Endless Winter',
    matches: ['climate collapse', 'global freezing', 'winter'],
    raw: climateRaw,
  },
]

export const SCENARIO_NARRATIVES = SCENARIO_SOURCES.map((source) => ({
  ...source,
  ...parseNarrative(source.raw),
}))

function randomItem(items) {
  return items[Math.floor(Math.random() * items.length)]
}

export function pickScenarioForCatastrophe(catastropheName) {
  const normalized = catastropheName.toLowerCase()
  const match = SCENARIO_NARRATIVES.find((scenario) =>
    scenario.matches.some((needle) => normalized.includes(needle)),
  )

  return match ?? randomItem(SCENARIO_NARRATIVES)
}
