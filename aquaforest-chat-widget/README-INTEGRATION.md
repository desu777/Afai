# Aquaforest Chat Widget - Integracja

## Pliki
- `aquaforest-chat-widget.umd.cjs` (306KB)
- `style.css` (16KB)

## WordPress

Wgraj pliki, dodaj do functions.php:

```php
add_action('wp_footer', function() { ?>
<link rel="stylesheet" href="<?php echo wp_upload_dir()['baseurl']; ?>/widget/style.css">
<div id="aquaforest-chat"></div>
<script src="<?php echo wp_upload_dir()['baseurl']; ?>/widget/aquaforest-chat-widget.umd.cjs"></script>
<script>
AquaforestChatWidget.render({
    containerId: 'aquaforest-chat',
    apiToken: 'aquaforest_dev_token_2025',
    apiUrl: 'https://aiagent.aquaforest.eu'
});
</script>
<?php });
```

## HTML

Przed `</body>`:

```html
<link rel="stylesheet" href="/path/style.css">
<div id="aquaforest-chat"></div>
<script src="/path/aquaforest-chat-widget.umd.cjs"></script>
<script>
AquaforestChatWidget.render({
    containerId: 'aquaforest-chat',
    apiToken: 'aquaforest_dev_token_2025',
    apiUrl: 'https://aiagent.aquaforest.eu'
});
</script>
```

## Opcje

```javascript
AquaforestChatWidget.render({
    containerId: 'aquaforest-chat',
    apiToken: 'token',
    apiUrl: 'https://aiagent.aquaforest.eu',
    position: 'bottom-right' // lub 'bottom-left'
});
```

## Język

- URL z `/pl/` → polski
- Inne URL → angielski

