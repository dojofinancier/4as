# Styling Migration Plan: Hardcoded Colors → Design System

## Current State Analysis

### Issues Identified:
1. **Hardcoded Colors**: 54+ instances of `#00746b` and `#005a52` throughout components
2. **Hardcoded Grays**: 165+ instances of `bg-gray-*`, `text-gray-*`, `border-gray-*`
3. **Tailwind Config**: Not configured to use CSS variables from `global.css`
4. **Inconsistent Styling**: Mix of inline Tailwind classes and hardcoded hex values
5. **Prose Styles**: Hardcoded colors in prose classes

### Files Requiring Updates:
- **14 component files** in `src/components/`
- **tailwind.config.js** - needs CSS variable integration
- **src/index.css** - has hardcoded colors in `.cta-button` and prose styles

## Color Mapping Strategy

### Primary Colors:
- `#00746b` → `bg-primary` / `text-primary` / `border-primary`
- `#005a52` → `hover:bg-primary` (darker variant) or custom hover class
- Current primary in CSS: `175.3448 100.0000% 22.7451%` (teal/green)

### Gray Scale Mapping:
- `bg-gray-50` → `bg-background` (80.0000 33.3333% 96.4706%)
- `bg-gray-100` → `bg-muted` (0 0% 94.1176%)
- `bg-gray-200` → `bg-border` or custom muted variant
- `bg-gray-300` → `bg-muted` (disabled states)
- `text-gray-900` → `text-foreground` (0 0% 0%)
- `text-gray-700` → `text-foreground` with opacity or `text-muted-foreground`
- `text-gray-600` → `text-muted-foreground` (0 0% 20%)
- `text-gray-500` → `text-muted-foreground` with opacity
- `border-gray-200` → `border-border` or `border-muted`
- `border-gray-300` → `border-border`

### White/Black:
- `bg-white` → `bg-card` (0 0% 100%)
- `text-white` → `text-primary-foreground` or `text-card-foreground`

## Migration Approach

### Phase 1: Configure Tailwind (Foundation)
1. Update `tailwind.config.js` to extend theme with CSS variables
2. Map CSS variables to Tailwind color system
3. Test that Tailwind classes work with CSS variables

### Phase 2: Update Global Styles
1. Update `src/index.css` to use design system colors
2. Replace hardcoded colors in `.cta-button` class
3. Update prose styles to use CSS variables

### Phase 3: Component Migration (Systematic)
**Priority Order:**
1. Core components (CourseSelection, Questionnaire wrapper)
2. Form components (PersonalInfo, HelpTypeSelection, WhenNeededSelection)
3. Content components (CourseBlogPost, GeneralArticle)
4. Utility components (ProgressBar, NotFound, etc.)
5. Application components (TutorApplication, ThankYou)

### Phase 4: Testing & Refinement
1. Visual regression testing
2. Dark mode compatibility check (if applicable)
3. Responsive design verification
4. Accessibility contrast checks

## Detailed Component Changes

### Common Patterns to Replace:

#### Primary Buttons:
```tsx
// Before:
className="bg-[#00746b] hover:bg-[#005a52] text-white"

// After:
className="bg-primary hover:bg-primary/90 text-primary-foreground"
```

#### Backgrounds:
```tsx
// Before:
className="bg-gray-50"

// After:
className="bg-background"
```

#### Text Colors:
```tsx
// Before:
className="text-gray-900"
className="text-gray-700"
className="text-gray-600"

// After:
className="text-foreground"
className="text-foreground/90"
className="text-muted-foreground"
```

#### Borders:
```tsx
// Before:
className="border-gray-200"
className="border-gray-300"

// After:
className="border-border"
className="border-muted"
```

#### Focus States:
```tsx
// Before:
className="focus:border-[#00746b] focus:ring-[#00746b]"

// After:
className="focus:border-primary focus:ring-primary"
```

## Implementation Steps

### Step 1: Update Tailwind Config
- Extend theme.colors to use CSS variables
- Configure opacity variants
- Add custom color utilities

### Step 2: Create Utility Classes (Optional)
- Consider creating reusable button classes
- Create form input classes
- Standardize spacing/sizing

### Step 3: Component-by-Component Migration
- Start with one component
- Test thoroughly
- Move to next component
- Maintain consistency

### Step 4: Cleanup
- Remove unused hardcoded colors
- Update documentation
- Verify all instances replaced

## Benefits After Migration

1. **Consistency**: All colors come from single source of truth
2. **Maintainability**: Change colors globally by updating CSS variables
3. **Dark Mode Ready**: CSS variables support dark mode switching
4. **Theme Support**: Easy to create alternate themes
5. **Better DX**: Semantic color names (`primary`, `muted`) vs hex codes

## Risk Mitigation

1. **Visual Changes**: The primary color might look slightly different
   - Solution: Test and adjust CSS variable if needed
2. **Breaking Changes**: Some components might need layout adjustments
   - Solution: Test each component individually
3. **Performance**: CSS variables are performant, minimal impact expected

## Estimated Effort

- **Tailwind Config**: 30 minutes
- **Global Styles**: 30 minutes  
- **Component Migration**: 2-3 hours (14 components × ~10-15 min each)
- **Testing**: 1 hour
- **Total**: ~4-5 hours

## Next Steps

1. Review and approve this plan
2. Start with Tailwind config update
3. Migrate components systematically
4. Test as we go

