# Test: Explore Internships UI Update
## Quick Testing Guide - 5 minutes

**What Changed**: Internship topics moved to collapsible filter at top, internships display horizontally in a grid

---

## Quick Test (5 minutes)

### Step 1: Start the Server
```bash
cd webintern
python app.py
```

### Step 2: Open Browser
```
http://localhost:5000/#/internships
```

### Step 3: Verify Layout

**Check These:**
- [ ] Title "Browse Internships" at top center
- [ ] "🔽 Filter by Sector" button visible
- [ ] Search box below button
- [ ] Internship cards displayed horizontally (4 per row on desktop)
- [ ] No sector tabs visible by default (they're hidden)

### Step 4: Test Collapse/Expand

**Click "Filter by Sector" button:**
- [ ] Sector tabs appear
- [ ] Chevron icon rotates down
- [ ] Tabs show all sectors with buttons

**Click button again:**
- [ ] Sector tabs disappear
- [ ] Chevron rotates back up

### Step 5: Test Search

**Type in search box:**
- [ ] "python" - Shows Python internships
- [ ] "react" - Shows React internships
- [ ] Results update in grid below
- [ ] Result count shows "Showing X of Y"

### Step 6: Test Mobile View

**In DevTools, toggle device toolbar (Ctrl+Shift+M):**
- [ ] Select iPhone 12
- [ ] Layout reflows properly
- [ ] Button still visible and clickable
- [ ] Cards stack nicely (1-2 per row)
- [ ] Search box accessible
- [ ] All text readable

### Step 7: Test Filters

**Expand filter and click a sector (e.g., "Python"):**
- [ ] Page shows only Python internships
- [ ] Results count updates
- [ ] Cards update in grid
- [ ] Pagination works

---

## Expected Behavior

### Desktop View (1920x1080):
```
[Header: Browse Internships]
                ↓
[🔽 Filter by Sector ▼]  ← Button, filter tabs hidden
                ↓
[🔍 Search Internships...]
       Showing 1-12 of 476
                ↓
[Card1] [Card2] [Card3] [Card4]
[Card5] [Card6] [Card7] [Card8]
[Card9] [Card10][Card11][Card12]
                ↓
      ← 1 2 3 4 5 →
```

### Mobile View (375x812):
```
[Header: Browse Internships]
                ↓
[🔽 Filter by Sector ▼]
                ↓
[🔍 Search Internships...]
                ↓
[Card1]
[Card2]
[Card3]
[Card4]
(scroll down for more)
```

---

## Troubleshooting

### Problem: Filter button doesn't toggle
**Solution**:
1. Check DevTools console (F12) for errors
2. Ensure JavaScript is enabled
3. Clear browser cache (Ctrl+Shift+Delete)
4. Reload page (F5)

### Problem: Cards not displaying in grid
**Solution**:
1. Wait for internships to load
2. Check DevTools Network tab for API errors
3. Verify server is running
4. Check console for JavaScript errors

### Problem: Search not working
**Solution**:
1. Make sure you clicked in search box
2. Wait 300ms for debounce
3. Check console for fetch errors
4. Try clearing search and trying again

### Problem: Mobile view broken
**Solution**:
1. Clear cache
2. Hard refresh (Ctrl+Shift+F5)
3. Try different device in DevTools
4. Check CSS media queries aren't conflicting

---

## Performance Check

**Should be fast:**
- ✅ Page loads in <2 seconds
- ✅ Internship cards appear without lag
- ✅ Toggle animation smooth (no jank)
- ✅ Search responds in <500ms
- ✅ Filter click instant

**If slow:**
1. Check network tab (slow API?)
2. Check console for errors
3. Check DevTools performance tab
4. Restart Flask server

---

## Browser Testing

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ | Should work perfectly |
| Firefox | ✅ | Should work perfectly |
| Safari | ✅ | Should work perfectly |
| Edge | ✅ | Should work perfectly |
| Mobile Chrome | ✅ | Should work perfectly |
| Mobile Safari | ✅ | Should work perfectly |

---

## Verification Checklist

When all of these pass, the UI is working correctly:

- [ ] Layout is vertical (not horizontal)
- [ ] Internships display in horizontal grid
- [ ] Filter button collapsible
- [ ] Filter hides by default
- [ ] Toggle button works (click to show/hide)
- [ ] Chevron rotates on click
- [ ] Search box functional
- [ ] Pagination working
- [ ] Mobile view responsive
- [ ] No console errors
- [ ] No performance issues

---

## Success Criteria

✅ **Test Passes If:**
1. All layout elements visible and properly positioned
2. Filter toggle works smoothly
3. Internships display horizontally
4. Mobile view is responsive
5. Search and filtering work
6. No JavaScript errors
7. Performance is good

---

## What to Look For

### Good Signs ✅:
- Clean, organized layout
- Filters easily accessible
- Internships easy to browse
- Mobile view scales properly
- Smooth animations
- Fast response time

### Bad Signs ❌:
- Overlapping elements
- Things out of alignment
- Slow to load
- Broken on mobile
- Console errors
- Buttons don't respond

---

## Next Steps

If tests pass:
1. ✅ Changes are working correctly
2. Ready to commit to Git
3. Can push to production

If tests fail:
1. Check console for errors
2. Restart Flask server
3. Clear browser cache
4. Try different browser
5. Check with agent if issues persist

---

## Time Estimate

- **Full test**: 5-10 minutes
- **Quick check**: 2-3 minutes
- **Mobile test**: 3-5 minutes

---

## Questions?

If anything seems broken:
1. Take a screenshot
2. Check browser console (F12)
3. Look at error messages
4. Restart Flask: `Ctrl+C` then `python app.py`

---

**You're ready to test! Open the browser and follow the steps above. 🚀**

