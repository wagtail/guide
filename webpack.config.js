const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
const postcssPresetEnv = require('postcss-preset-env');

const source = path.resolve(path.join('apps', 'frontend', 'static_src'));
const destination = path.resolve(path.join('apps', 'frontend', 'static'));

const config = {
    entry: {
        blocking: path.resolve(source, 'js', 'blocking.js'),
        main: [
            path.join(source, 'js', 'main.js'),
            path.join(source, 'scss', 'main.scss'),
        ],
    },
    output: {
        path: destination,
        publicPath: '/static/',
        filename: '[name]-[fullhash].js',
        clean: true,
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'],
                    },
                },
            },
            {
                test: /\.(scss|css)$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: true,
                        },
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            sourceMap: true,
                            postcssOptions: {
                                plugins: [
                                    postcssPresetEnv({
                                        enableClientSidePolyfills: false,
                                    }),
                                ],
                            },
                        },
                    },
                    'sass-loader',
                ],
            },
        ],
    },
    resolve: {
        alias: {
            '~fonts': path.resolve(path.join(source, 'fonts')),
            '~images': path.resolve(path.join(source, 'images')),
        },
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: '[name]-[fullhash].css',
        }),
        new CopyWebpackPlugin({
            patterns: [
                {
                    from: path.join(source, 'images'),
                    to: path.join(destination, 'images'),
                },
            ],
        }),
        new WebpackManifestPlugin({ publicPath: '' }),
    ],
};

module.exports = (env, argv) => {
    if (argv.mode === 'development') {
        config.devtool = 'inline-source-map';
    }
    return config;
};
