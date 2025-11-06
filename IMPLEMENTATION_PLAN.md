# Landing Page Integration - Implementation Plan

## Overview
This plan implements the integration between the landing page and the app to redirect students to course reservation pages when courses are available.

## Key Decisions

### 1. Availability Check Timing
**Recommendation: Check during course selection + re-check at submission**

- **During Selection**: Filter courses by `active = true` in database query (immediate feedback)
- **On Course Select**: Check availability via API in background (non-blocking, show loading state)
- **At Submission**: Re-check availability (in case it changed) and redirect if available

**Rationale**:
- Users get immediate feedback if course is unavailable
- Reduces submission-time load (webhook + availability check + redirect)
- Still validates at submission in case availability changed
- Better UX - users know upfront if they can proceed

### 2. Form Data Structure
- Store `courseCode` and `courseSlug` internally for availability check/redirect
- Keep sending `course` (full text) to webhook for backward compatibility
- Store course display text separately for webhook payload

### 3. Error Handling
- Availability check failure → Show thank you page (graceful degradation)
- Network errors → Log and proceed to thank you page
- API errors → Treat as unavailable

## Implementation Steps

### Step 1: Update Types and Database Schema

**File**: `src/types.ts`

**Changes**:
1. Update `Course` interface:
   - Remove `full_name: string`
   - Add `title_fr: string`
   - Add `slug: string`
   - Add `active: boolean` (optional, for filtering)

2. Update `FormData` interface:
   - Keep `course: string` (for webhook compatibility)
   - Add `courseCode: string`
   - Add `courseSlug: string | null`
   - Add `courseDisplayText: string` (for webhook)

3. Add new type:
   ```typescript
   export type Step = 'course' | 'helpType' | 'when' | 'name' | 'email' | 'thank-you' | 'unavailable';
   ```

4. Add availability check result type:
   ```typescript
   export interface CourseAvailability {
     available: boolean;
     slug: string | null;
     tutorsCount: number;
   }
   ```

---

### Step 2: Update Supabase Query

**File**: `src/lib/supabase.ts`

**Changes**:
1. Update `searchCourses` function:
   - Change search from `full_name` to `title_fr`
   - Query: `.or(\`title_fr.ilike.%${query}%,code.ilike.%${query}%\`)`
   - Select fields: `id, code, title_fr, slug, institution, active`
   - Add filter: `.eq('active', true)` to only show active courses

2. Add new function `checkCourseAvailability`:
   ```typescript
   export async function checkCourseAvailability(courseCode: string): Promise<CourseAvailability> {
     try {
       const response = await fetch(
         `https://app.carredastutorat.com/api/check-course-availability?courseCode=${encodeURIComponent(courseCode)}`
       );
       
       if (!response.ok) {
         console.error('Availability check failed:', response.status);
         return { available: false, slug: null, tutorsCount: 0 };
       }
       
       return await response.json();
     } catch (error) {
       console.error('Error checking course availability:', error);
       return { available: false, slug: null, tutorsCount: 0 };
     }
   }
   ```

---

### Step 3: Update Course Selection Component

**File**: `src/components/CourseSelection.tsx`

**Changes**:
1. Update `CourseSelectionProps`:
   ```typescript
   interface CourseSelectionProps {
     onSelect: (course: { code: string; slug: string; displayText: string }) => void;
     onNext: () => void;
   }
   ```

2. Update `handleCourseSelect`:
   - Change `course.full_name` to `course.title_fr`
   - Create display text: `${course.title_fr} (${course.code}${course.institution ? ' - ' + course.institution : ''})`
   - Call `onSelect` with object: `{ code, slug, displayText }`
   - Store course object in local state for display

3. Update dropdown display:
   - Change `course.full_name` to `course.title_fr` in display

4. Add availability check after selection (optional enhancement):
   - Could add a loading state while checking
   - Could show warning if unavailable
   - But keep it non-blocking - user can still proceed

---

### Step 4: Update Questionnaire Component

**File**: `src/components/Questionnaire.tsx`

**Changes**:
1. Update form data initialization to include new fields:
   ```typescript
   const [formData, setFormData] = useState<FormData>({
     course: '',           // For webhook (full text)
     courseCode: '',       // For availability check
     courseSlug: null,    // For redirect
     courseDisplayText: '', // For display
     helpTypes: [],
     whenNeeded: '',
     name: '',
     email: ''
   });
   ```

2. Update `CourseSelection` usage:
   - Change `onSelect` to store all three fields: `code`, `slug`, `displayText`
   - Update `formData.course` with `displayText` (for webhook)
   - Update `formData.courseCode` and `formData.courseSlug`

3. Update `submitForm` function:
   - Keep webhook submission as-is (sends `course` field)
   - After successful webhook submission, call availability check:
     ```typescript
     const availability = await checkCourseAvailability(formData.courseCode);
     ```
   - If `availability.available === true`:
     - Redirect: `window.location.href = \`https://app.carredastutorat.com/cours/${availability.slug}/reservation?code=${formData.courseCode}&source=lp\`;`
     - Return early (don't show thank you page)
   - If `availability.available === false`:
     - Set step to `'unavailable'`
   - If error (catch block):
     - Show thank you page (graceful degradation)

4. Update step handling to include `'unavailable'` case:
   ```typescript
   case 'unavailable':
     return <CourseUnavailable courseCode={formData.courseCode} onBackToSearch={() => setCurrentStep('course')} />;
   ```

5. Import `checkCourseAvailability` from `../lib/supabase`

---

### Step 5: Create Course Unavailable Component

**File**: `src/components/CourseUnavailable.tsx` (NEW FILE)

**Requirements**:
- Similar layout to `ThankYou.tsx` (logo, centered content, footer)
- Display message: "Désolé, il n'y a actuellement aucun tuteur disponible pour ce cours."
- Add button: "Rechercher un autre cours" that calls `onBackToSearch`
- Accept props: `courseCode: string` and `onBackToSearch: () => void`
- Use same styling (gray-50 background, green accent #00746b)
- Display course code in message (optional)

**Structure**:
```typescript
interface CourseUnavailableProps {
  courseCode: string;
  onBackToSearch: () => void;
}

export function CourseUnavailable({ courseCode, onBackToSearch }: CourseUnavailableProps) {
  // Similar structure to ThankYou.tsx
  // Use AlertCircle or XCircle icon from lucide-react
  // Show message and button
}
```

---

## Implementation Order

1. ✅ Step 1: Update Types
2. ✅ Step 2: Update Supabase Query
3. ✅ Step 3: Update Course Selection
4. ✅ Step 4: Update Questionnaire
5. ✅ Step 5: Create Unavailable Component

## Testing Checklist

### Unit Testing
- [ ] Course search returns courses with `title_fr`
- [ ] Course search filters by `active = true`
- [ ] Availability check function handles errors gracefully
- [ ] Form data stores course code and slug correctly

### Integration Testing
- [ ] User can search and select courses
- [ ] Course selection stores all required fields
- [ ] Webhook receives `course` field (backward compatible)
- [ ] Availability check is called after webhook
- [ ] Redirect works when course is available
- [ ] Unavailable page shows when no tutors
- [ ] Error handling shows thank you page on failure

### End-to-End Testing
- [ ] Full flow: Search → Select → Submit → Redirect (if available)
- [ ] Full flow: Search → Select → Submit → Unavailable (if no tutors)
- [ ] Error case: API down → Thank you page
- [ ] URL parameters are correct: `code` and `source=lp`

## Edge Cases Handled

1. **Availability check fails**: Show thank you page
2. **Network error**: Show thank you page
3. **API returns unavailable**: Show unavailable page
4. **Course selected but no slug**: Unavailable page (slug is null)
5. **User goes back and changes course**: Form data updates correctly

## Backward Compatibility

- ✅ Webhook still receives `course` field (full text)
- ✅ Existing webhook payload structure unchanged
- ✅ No breaking changes to Make.com workflow

## Notes

- The `course` field in FormData is kept for webhook compatibility
- The availability check happens after webhook submission (as requested)
- Filtering by `active = true` happens in database query (during search)
- Error handling is graceful - always shows a page (thank you or unavailable)



