<?php

// Run with: php tests/template-output.php
define('APP_PATH', dirname(__DIR__) . '/application/');
require dirname(__DIR__) . '/thinkphp/base.php';
require dirname(__DIR__) . '/thinkphp/helper.php';
require APP_PATH . 'common.php';

set_exception_handler(function (Throwable $error) {
    fwrite(STDERR, $error->getMessage() . "\n");
    exit(1);
});

think\Config::set('fastadmin', ['adminskin' => '', 'show_submenu' => false, 'multiplenav' => false]);
think\Config::set('site', ['version' => 'test', 'cdnurl' => '']);
think\Config::set('lang_switch_on', false);

function renderPartial($path, $vars)
{
    ob_start();
    $template = new think\Template(['tpl_cache' => false, 'cache_prefix' => 'template-output-test-']);
    $template->display(file_get_contents(APP_PATH . $path), $vars);
    return ob_get_clean();
}

$text = '</script><script>alert("test")</script><>&\' 中文';
$config = ['site' => ['version' => 'test', 'name' => $text], 'text' => $text];
$vars = ['config' => $config, 'title' => $text, 'site' => ['name' => $text]];

foreach (['admin', 'index'] as $module) {
    $html = renderPartial($module . '/view/common/meta.html', $vars);
    if (!preg_match('/var require = \{\s*config:\s*(.*?)\s*\};/s', $html, $matches)) {
        throw new RuntimeException($module . ': missing inline config');
    }
    if (json_decode($matches[1], true, 512, JSON_THROW_ON_ERROR) !== $config) {
        throw new RuntimeException($module . ': config did not round-trip');
    }
    if (strpbrk($matches[1], '<>&\'') !== false) {
        throw new RuntimeException($module . ': unsafe inline JSON characters');
    }
    if (strpos($html, '<title>' . htmlentities($text)) === false) {
        throw new RuntimeException($module . ': title escaping changed');
    }
}

$vars['admin'] = ['avatar' => '/assets/img/avatar.png', 'nickname' => $text, 'logintime' => 0];
$vars['menulist'] = '<li><a href="/dashboard?ref=addtabs">Dashboard</a></li>';
$vars['navlist'] = '<li role="presentation"><a href="#con_1">Dashboard</a></li>';
foreach (['menu' => 'menulist', 'header' => 'navlist'] as $partial => $variable) {
    $html = renderPartial('admin/view/common/' . $partial . '.html', $vars);
    if (strpos($html, $vars[$variable]) === false) {
        throw new RuntimeException($partial . ': generated menu HTML was escaped');
    }
    if (strpos($html, htmlentities($text)) === false || strpos($html, $text) !== false) {
        throw new RuntimeException($partial . ': nickname escaping changed');
    }
}

echo "PASS: inline config round-trips safely, menus render as HTML, and text stays escaped.\n";
