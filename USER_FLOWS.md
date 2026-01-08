# FunBookies User Flows

## Overview

FunBookies serves two user types with connected but distinct experiences:

1. **Teachers** - Set up classes, assign students, track progress
2. **Parents** - Practice reading with their child at home

The key flow: **School provides → Parent practices → Teacher monitors**

---

## User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                         TEACHER FLOW                            │
│                                                                 │
│  1. Create class                                                │
│  2. Import/add students                                         │
│  3. Run initial assessments (in class)                          │
│  4. Generate parent invite links                                │
│  5. Monitor progress dashboard                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Invite link
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PARENT FLOW                             │
│                                                                 │
│  1. Click invite link from teacher                              │
│  2. See child's name, level, recommended books                  │
│  3. Practice: read books, do activities                         │
│  4. Progress syncs back to teacher (future: cloud sync)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Teacher Experience (`/classroom`)

### Features

| Feature | Description |
|---------|-------------|
| **Class Setup** | Create classes, set grade level |
| **Student Import** | CSV upload, manual add, (future: Google Classroom) |
| **Bulk Assessment** | Run assessments for whole class |
| **Progress Dashboard** | Class-level analytics, struggling students flagged |
| **Parent Links** | Generate unique links for each student's parent |
| **Reports** | Export progress for admin/parents |

### Screens

1. **Class List** - All classes, student counts
2. **Class View** - Students grid, level distribution
3. **Student Detail** - Individual progress (same as current profile)
4. **Assessment Mode** - Streamlined for running with students
5. **Parent Links** - Generate/manage invite links

### Teacher Dashboard Metrics

- Students by level (bar chart)
- Students needing attention (below grade level)
- Recent activity (who's practicing at home)
- Class average progress over time

---

## Parent Experience (`/home`)

### Features

| Feature | Description |
|---------|-------------|
| **Single Child Focus** | No student picker, just their child |
| **Level Display** | Clear indication of reading level |
| **Recommended Books** | Curated list at child's level |
| **Daily Practice** | Suggested activities, streaks |
| **Simple Progress** | "Emma read 3 books this week" |

### Screens

1. **Home** - Child's avatar, level, "What to do today"
2. **Books** - Filtered to appropriate level
3. **Activities** - Practice games at their level
4. **Progress** - Simple stats, celebration of achievements

### Parent Home Layout

```
┌─────────────────────────────────────────┐
│  👋 Welcome back!                       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  🦊 Emma                         │   │
│  │  Level B2 - CVC Short o, u, e   │   │
│  │  🔥 5 day streak                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  📖 Today's Reading                     │
│  ┌─────┐ ┌─────┐ ┌─────┐              │
│  │Book1│ │Book2│ │Book3│              │
│  └─────┘ └─────┘ └─────┘              │
│                                         │
│  🎮 Practice Activities                 │
│  [Sight Words] [Word Builder] [Blend]  │
│                                         │
│  📊 This Week                           │
│  Books read: 3  │  Activities: 7       │
│                                         │
└─────────────────────────────────────────┘
```

---

## Data Architecture

### Current (MVP - Local Storage)

- All data stored in IndexedDB on device
- Parent link contains student info encoded
- No sync between devices

### Future (Cloud Sync)

```
Teacher Device ←→ Cloud ←→ Parent Device
     │                          │
     └── Student roster         └── Practice data
         Assessment results         Book completions
         Level assignments          Activity scores
```

---

## Entry Points

| URL | Experience | Description |
|-----|------------|-------------|
| `/` | Landing | Marketing, choose parent or teacher |
| `/home` | Parent | Single-child focused practice |
| `/classroom` | Teacher | Class management dashboard |
| `/dashboard` | Legacy | Current dashboard (deprecate) |

---

## Parent Invite Link Format

```
https://funbookies.com/home?
  student=Emma
  &level=B2
  &teacher=Mrs.+Smith
  &class=2nd+Grade
```

For MVP, the link just pre-fills the student info. Parent's device stores progress locally.

Future: Links contain encrypted student ID for cloud sync.

---

## Implementation Phases

### Phase 1: MVP (Current Sprint)
- [x] Parent home page (`/home`)
- [x] Teacher classroom page (`/classroom`)
- [ ] Parent invite link generation
- [ ] Basic progress display

### Phase 2: Enhanced
- [ ] CSV import for teachers
- [ ] Class-level analytics
- [ ] Parent progress reports
- [ ] Multiple children per parent

### Phase 3: Cloud Sync
- [ ] User accounts
- [ ] Real-time sync
- [ ] Google Classroom integration
- [ ] School admin dashboard

---

## Key Differences Summary

| Aspect | Parent (`/home`) | Teacher (`/classroom`) |
|--------|------------------|------------------------|
| **Focus** | Single child | Whole class |
| **Tone** | Warm, encouraging | Professional, efficient |
| **Primary Action** | "Read together" | "Monitor progress" |
| **Complexity** | Minimal UI | Full dashboard |
| **Data Entry** | None (from invite) | Import/manage roster |

---

*Last Updated: January 2025*
