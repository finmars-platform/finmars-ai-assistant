const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
module.exports = {
    entry: './src/js/finmars-extension.js',
    output: {
        filename: 'finmars-extension.bundle.js',
        path: path.resolve(__dirname, 'dist')
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader, // Extracts CSS into separate files
                    'css-loader' // Translates CSS into CommonJS
                ]
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'finmars-extension.bundle.css'
        })
    ]
};
