# 🐠 Aquaforest Chat Widget - Integration

## Files to Host
Upload these 2 files to your web server:
- `aquaforest-chat-widget.umd.cjs`
- `style.css`

## Integration Code
Add this to your HTML (before `</body>`):

```html
<!-- Widget CSS -->
<link rel="stylesheet" href="dist/style.css">

<!-- Widget Container -->
<div id="aquaforest-chat"></div>

<!-- Widget Script -->
<script src="dist/aquaforest-chat-widget.umd.cjs"></script>
<script>
AquaforestChatWidget.render({
    containerId: 'aquaforest-chat',
    apiToken: 'aquaforest_dev_token_2025',
    apiUrl: 'https://aiagent.aquaforest.eu',
    position: 'bottom-right'
});
</script>
```

## That's It!
The widget will appear as a floating chat button in the bottom-right corner.

---

### Configuration Options
- `position`: `'bottom-right'` or `'bottom-left'`  
- `theme`: `'aquaforest'` (default)


### File Size
- Total: ~855KB (~266KB gzipped)
- No impact on page load speed

