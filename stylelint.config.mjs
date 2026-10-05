/**
 * Stylelint configuration.
 *
 * Extends the shared Wagtail config, with a few project-specific overrides.
 */
export default {
  extends: ['@wagtail/stylelint-config-wagtail'],
  rules: {
    /**
     * Only require mixins with no block of their own (e.g. `@include fs(s)`) to
     * come before declarations. The shared config also requires block-level
     * includes such as `@include media-query(large) { … }` to come first, but
     * moving those above base declarations flips the CSS cascade at the
     * configured breakpoints.
     */
    'order/order': [
      { type: 'at-rule', name: 'include', hasBlock: false },
      'declarations',
    ],
    'scale-unlimited/declaration-strict-value': [
      ['color', '/-color/', 'fill', 'stroke'],
      {
        ignoreValues: [
          'currentColor',
          'inherit',
          'initial',
          'none',
          'unset',
          'transparent',
          'Canvas',
          'CanvasText',
          'LinkText',
          'VisitedText',
          'ActiveText',
          'ButtonFace',
          'ButtonText',
          'ButtonBorder',
          'Field',
          'FieldText',
          'Highlight',
          'HighlightText',
          'SelectedItem',
          'SelectedItemText',
          'Mark',
          'MarkText',
          'GrayText',
          'AccentColor',
          'AccentColorText',
        ],
      },
    ],
    /**
     * Disabled: this project deliberately writes BEM selectors with the SCSS
     * parent selector (e.g. `.block { &__element {} }`). Enforcing this rule
     * would require rewriting every component’s BEM selectors, which is out of
     * scope for the Stylelint upgrade.
     */
    'scss/selector-no-union-class-name': null,
  },
};
