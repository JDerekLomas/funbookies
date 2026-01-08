# Comprehensive Phonics System Vision

## Overview

A teacher-assigned, parent-delivered home practice system. Teachers/schools provide the platform to families, assign practice, and monitor progress. Parents facilitate nightly sessions with their children.

## The Model

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   TEACHER   │ ──────▶ │   PARENT    │ ──────▶ │   CHILD     │
│  Assigns    │         │  Facilitates│         │  Practices  │
│  Monitors   │ ◀────── │  Reports    │ ◀────── │             │
└─────────────┘         └─────────────┘         └─────────────┘
```

## Role Requirements

### Teacher Dashboard
- Create classroom, add students
- Set each student's current phonics level (or use assessment)
- Assign weekly practice (specific books + activities)
- View completion reports & progress over time
- Flag struggling students for intervention
- Send home practice recommendations

### Parent Portal
- Join classroom via invite link from teacher
- See "Tonight's Practice" clearly on login
- Step-by-step session guide with timing
- Mark sessions complete, note struggles
- Target: ~15 min/night, 3-4 nights/week

### Student Experience
- Clear "what to do today"
- Age-appropriate interface
- Rewards/streaks for consistency
- Fun, not homework-feeling

## Nightly Session Flow

```
Parent opens app → "Emma's Practice for Tuesday"

┌────────────────────────────────────────┐
│  Tonight's Practice (15 min)           │
│                                        │
│  1. 📖 Read: "Frog and Crab" (5 min)   │
│     Level B4 - Consonant Blends        │
│     [Start Reading]                    │
│                                        │
│  2. 🎯 Practice: Blend Words (5 min)   │
│     Build words with bl-, cr-, fr-     │
│     [Start Activity]                   │
│                                        │
│  3. ⭐ Review: Yesterday's words       │
│     Quick check on retention           │
│     [Quick Review]                     │
│                                        │
│  [✓ Mark Session Complete]             │
└────────────────────────────────────────┘
```

## Components to Build

### Phase 1: Parent-Child Experience (Current Focus)
- [x] Assessment to place child at level
- [x] Decodable books organized by level
- [x] Parent tips in reader
- [ ] "Tonight's Practice" guided session view
- [ ] Session completion tracking
- [ ] Progress visualization for parents
- [ ] Streak/reward system

### Phase 2: Teacher-Parent Connection
- [ ] Teacher creates classroom
- [ ] Parent invite link generation
- [ ] Student assignment to classrooms
- [ ] Teacher sets/overrides student levels
- [ ] Completion reports visible to teacher

### Phase 3: Teacher Assignment System
- [ ] Teacher assigns specific books/activities
- [ ] Weekly practice plans
- [ ] Custom assignment creation
- [ ] Bulk assignment to groups
- [ ] Due dates and reminders

### Phase 4: Analytics & Reporting
- [ ] Progress reports for teachers
- [ ] Class-wide analytics
- [ ] Individual student deep-dives
- [ ] Struggling student alerts
- [ ] Parent engagement metrics

## What Makes This Different

1. **Teacher-Initiated**: Schools provide the system, not random parents finding it
2. **Structured Sessions**: Not "here's some books" but "here's tonight's 15-minute session"
3. **Accountability Loop**: Teachers see completion, can follow up
4. **Low Parent Burden**: Clear instructions, short sessions, no expertise needed
5. **Curriculum Aligned**: Matches what's being taught in school (UFLI-aligned)

## Integration Considerations

- Google Classroom integration for roster sync
- ClassDojo for notifications/messaging
- Clever for SSO in schools
- Export progress to SIS systems

## Open Questions

1. How do teachers currently communicate homework to parents?
2. What's the right session frequency? (3x/week? 5x/week?)
3. Should sessions be assigned by day or flexible "do 3 this week"?
4. How much teacher customization vs. auto-generated practice?
5. Offline support needed for families without reliable internet?

---

*This document captures the vision discussed on 2026-01-09. Focus remains on parent-child experience first, with teacher features to follow.*
